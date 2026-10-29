// Read right A through OpenVR; forward an F8 pulse only to the focused game.
// No DLL injection, process-memory writes, global bindings, or startup registration.
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <openvr.h>
#include <cstdio>
#include <string>

struct Edge {
    bool previous = true; // Require release before first activation.
    bool step(bool down, bool focused) {
        bool fire = down && !previous && focused;
        previous = down;
        return fire;
    }
};
static bool key(bool down) {
    INPUT input{}; input.type = INPUT_KEYBOARD;
    input.ki.wVk = VK_F8; input.ki.dwFlags = down ? 0 : KEYEVENTF_KEYUP;
    return SendInput(1, &input, sizeof(input)) == 1;
}
static DWORD findGame(const std::wstring& expected) {
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if(snapshot == INVALID_HANDLE_VALUE) return 0;
    PROCESSENTRY32W entry{}; entry.dwSize = sizeof(entry); DWORD found = 0;
    if(Process32FirstW(snapshot, &entry)) do {
        if(_wcsicmp(entry.szExeFile, L"GalGun2-Win64-Shipping.exe")) continue;
        HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, entry.th32ProcessID);
        if(!process) continue;
        wchar_t path[32768]; DWORD count = 32768;
        if(QueryFullProcessImageNameW(process, 0, path, &count) && !_wcsicmp(path, expected.c_str())) found = entry.th32ProcessID;
        CloseHandle(process);
        if(found) break;
    } while(Process32NextW(snapshot, &entry));
    CloseHandle(snapshot); return found;
}
int wmain(int argc, wchar_t** argv) {
    if(argc > 1 && !wcscmp(argv[1], L"--self-test")) {
        Edge e;
        bool pass = !e.step(true,true) && !e.step(false,true) && e.step(true,true)
            && !e.step(true,true) && !e.step(false,true) && !e.step(true,false)
            && !e.step(true,true) && !e.step(false,true) && e.step(true,true);
        puts(pass ? "PASS: release, rising edge, held input, focus-loss suppression" : "FAIL");
        return pass ? 0 : 1;
    }
    if(argc < 2) { puts("Usage: EkoroLaserBridge.exe GAME_ROOT [--probe]"); return 2; }
    bool probe = argc > 2 && !wcscmp(argv[2], L"--probe");
    HANDLE mutex = CreateMutexW(nullptr, FALSE, L"Local\\GalGun2EkoroLaserBridge");
    if(!mutex || GetLastError() == ERROR_ALREADY_EXISTS) return 3;
    std::wstring root = argv[1];
    const auto exe = root + L"\\GalGun2\\Binaries\\Win64\\GalGun2-Win64-Shipping.exe";
    DWORD pid = findGame(exe);
    if(!pid) { puts("Start GalGun2 before the bridge."); CloseHandle(mutex); return 4; }
    HANDLE process = OpenProcess(SYNCHRONIZE, FALSE, pid);
    if(!process) { CloseHandle(mutex); return 5; }
    const auto dllpath = root + L"\\Engine\\Binaries\\ThirdParty\\OpenVR\\OpenVRv1_0_10\\Win64\\openvr_api.dll";
    HMODULE dll = LoadLibraryExW(dllpath.c_str(), nullptr, LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_SYSTEM32);
    if(!dll) { puts("Could not load the game's OpenVR runtime DLL."); CloseHandle(process); CloseHandle(mutex); return 6; }
    auto init = reinterpret_cast<uint32_t(__cdecl*)(vr::EVRInitError*, vr::EVRApplicationType, const char*)>(GetProcAddress(dll,"VR_InitInternal2"));
    auto shutdown = reinterpret_cast<void(__cdecl*)()>(GetProcAddress(dll,"VR_ShutdownInternal"));
    auto get = reinterpret_cast<void*(__cdecl*)(const char*,vr::EVRInitError*)>(GetProcAddress(dll,"VR_GetGenericInterface"));
    if(!init || !shutdown || !get) { puts("Missing OpenVR exports."); return 7; }
    vr::EVRInitError error = vr::VRInitError_None;
    init(&error, vr::VRApplication_Background, nullptr);
    if(error) { printf("OpenVR init error %d\n",error); return 8; }
    auto system = static_cast<vr::IVRSystem*>(get(vr::IVRSystem_Version,&error));
    if(error || !system) { printf("OpenVR interface error %d\n",error); shutdown(); return 9; }
    printf("Bridge ready: PID %lu, right A -> F8, probe=%d\n",pid,probe); fflush(stdout);
    Edge edge; bool held = false, lastRaw = false, lastFocus = false;
    ULONGLONG releaseAt = 0, started = GetTickCount64();
    while(WaitForSingleObject(process,0) == WAIT_TIMEOUT) {
        const auto now = GetTickCount64();
        DWORD foreground = 0; GetWindowThreadProcessId(GetForegroundWindow(), &foreground);
        const bool focused = foreground == pid;
        auto device = system->GetTrackedDeviceIndexForControllerRole(vr::TrackedControllerRole_RightHand);
        vr::VRControllerState_t state{};
        bool valid = device != vr::k_unTrackedDeviceIndexInvalid && system->IsTrackedDeviceConnected(device)
            && system->GetControllerState(device,&state,sizeof(state));
        bool down = valid && (state.ulButtonPressed & vr::ButtonMaskFromId(vr::k_EButton_A));
        if(down != lastRaw || focused != lastFocus) {
            printf("A=%d focused=%d valid=%d\n",down,focused,valid); fflush(stdout);
            lastRaw=down; lastFocus=focused;
        }
        if(held && (now >= releaseAt || !focused || !valid)) { key(false); held=false; }
        if(edge.step(down, focused) && !probe && !held) {
            held=key(true); releaseAt=now+100;
            printf("F8 pulse sent=%d\n",held); fflush(stdout);
        }
        if(!valid) edge.previous=true; // No activation from reconnecting while held.
        if(probe && now-started >= 45000) break;
        Sleep(10);
    }
    if(held) key(false);
    shutdown(); FreeLibrary(dll); CloseHandle(process); CloseHandle(mutex);
    puts("Bridge stopped."); return 0;
}

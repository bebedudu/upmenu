"""
Audio Device Test Script
Run this to diagnose audio device issues
"""

print("="*60)
print("AUDIO DEVICE DIAGNOSTIC TEST")
print("="*60)

# Test 1: Check if required libraries are installed
print("\n1. Checking required libraries...")
try:
    from ctypes import cast, POINTER
    print("   ✓ ctypes available")
except ImportError as e:
    print(f"   ✗ ctypes NOT available: {e}")

try:
    from comtypes import CLSCTX_ALL
    print("   ✓ comtypes available")
except ImportError as e:
    print(f"   ✗ comtypes NOT available: {e}")
    print("   Install with: pip install comtypes")

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    print("   ✓ pycaw available")
except ImportError as e:
    print(f"   ✗ pycaw NOT available: {e}")
    print("   Install with: pip install pycaw")

# Test 2: Try to get audio device
print("\n2. Getting audio devices...")
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    
    devices = AudioUtilities.GetSpeakers()
    if devices:
        print(f"   ✓ Found speaker device: {devices}")
        print(f"   Device type: {type(devices)}")
        print(f"   Device attributes: {[attr for attr in dir(devices) if not attr.startswith('_')]}")
    else:
        print("   ✗ No speaker devices found")
except Exception as e:
    print(f"   ✗ Error getting devices: {e}")

# Test 3: Try to get volume interface
print("\n3. Getting volume interface...")
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
    
    devices = AudioUtilities.GetSpeakers()
    if devices:
        interface = None
        
        # Try different methods based on pycaw version
        if hasattr(devices, 'Activate'):
            print("   Using old pycaw API (Activate method)")
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        elif hasattr(devices, '_dev') and hasattr(devices._dev, 'Activate'):
            print("   Using new pycaw API (_dev.Activate method)")
            interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        elif hasattr(devices, 'activate'):
            print("   Using new pycaw API (activate method)")
            interface = devices.activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        else:
            print("   ✗ Cannot find Activate method")
            print(f"   Available methods: {[m for m in dir(devices) if 'activ' in m.lower()]}")
            
        if interface:
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            print(f"   ✓ Got volume interface: {volume}")
            
            # Test 4: Try to get current volume
            print("\n4. Getting current volume...")
            current_vol = volume.GetMasterVolumeLevelScalar()
            print(f"   ✓ Current volume: {int(current_vol * 100)}%")
            
            # Test 5: Try to check mute status
            print("\n5. Checking mute status...")
            is_muted = volume.GetMute()
            print(f"   ✓ Muted: {bool(is_muted)}")
            
            # Test 6: Try to change volume
            print("\n6. Testing volume change (setting to 50%)...")
            volume.SetMasterVolumeLevelScalar(0.5, None)
            new_vol = volume.GetMasterVolumeLevelScalar()
            print(f"   ✓ New volume: {int(new_vol * 100)}%")
            
            # Restore original volume
            volume.SetMasterVolumeLevelScalar(current_vol, None)
            print(f"   ✓ Restored volume to: {int(current_vol * 100)}%")
            
            print("\n" + "="*60)
            print("ALL TESTS PASSED - Audio should work in your application!")
            print("="*60)
    else:
        print("   ✗ No devices to test")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)

# List all audio sessions
print("\n\nBonus: Listing all audio sessions...")
try:
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process:
            print(f"   - {session.Process.name()}")
except Exception as e:
    print(f"   Error listing sessions: {e}")

input("\nPress Enter to exit...")

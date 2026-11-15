from ser.utils.service_names import get_full_name, get_short_name, get_service_file_path
from ser.utils.systemd import get_unit_path, _encode_dbus_path
from ser.utils.process_status import get_page_size_kb, clock_ticks_per_second

# Test service_names
assert get_full_name("hello-world") == "hello-world.ser.service", "FAIL: get_full_name"
assert get_short_name("hello-world.ser.service") == "hello-world", "FAIL: get_short_name"
assert str(get_service_file_path("hello-world.ser.service")) == "/etc/systemd/system/hello-world.ser.service"
print("service_names: OK")

# Test D-Bus path encoding (matches Rust encode_as_dbus_object_path)
encoded = _encode_dbus_path("hello-world.ser.service")
assert encoded == "hello_2dworld_2eser_2eservice", f"FAIL: got {encoded}"
path = get_unit_path("hello-world.ser.service")
assert path == "/org/freedesktop/systemd1/unit/hello_2dworld_2eser_2eservice", f"FAIL: got {path}"
print("systemd encoding: OK")

# Test /proc-based helpers (safe to call without root)
page_kb = get_page_size_kb()
assert page_kb > 0, "FAIL: page size"
tps = clock_ticks_per_second()
assert tps == 100, f"FAIL: unexpected tps {tps}"
print(f"process_status: page_size={page_kb} KB, tps={tps}")

print("\nAll unit tests passed!")

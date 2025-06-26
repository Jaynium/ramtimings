extends Control

var current_module: GameData.MemoryModule
var memory_controller: GameData.MemoryController
var game_data: GameData

var selected_option_index: int = 0
var options_list: Array = []

func _ready():
	game_data = GameData.new()
	setup_test_data()
	populate_frequency_options()
	populate_command_rate()
	populate_xmp_profiles()
	update_display()
	
	# Set focus to first option
	get_viewport().gui_focus_changed.connect(_on_focus_changed)

func setup_test_data():
	# Create a test module (in real implementation, would load from game state)
	current_module = GameData.MemoryModule.new(
		"GameSkill Blade Z Neo 3600",
		GameData.MemoryType.DDR4,
		GameData.MemoryIC.SAMSUNG_CDIE,
		2133, [15, 15, 15, 36],
		3600, [16, 19, 19, 39],
		1.35, 16, 38.0, 7
	)
	
	memory_controller = GameData.MemoryController.new(7, 1.5, true, true, 2, 1, 1.1, 1.25)
	
	# Set initial UI values
	setup_ui_values()

func populate_frequency_options():
	var freq_option = $BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/FrequencyOption/Value
	freq_option.clear()
	
	# Add frequency options based on memory type
	if current_module.memory_type == GameData.MemoryType.DDR4:
		var frequencies = [2133, 2400, 2666, 2800, 3000, 3200, 3333, 3466, 3600, 3733, 3866, 4000, 4133, 4266, 4400, 4533, 4600]
		for freq in frequencies:
			freq_option.add_item("DDR4-%d" % freq)
			if freq == current_module.current_speed:
				freq_option.selected = freq_option.get_item_count() - 1
	else:
		var frequencies = [4800, 5200, 5600, 6000, 6200, 6400, 6600, 6800, 7000, 7200]
		for freq in frequencies:
			freq_option.add_item("DDR5-%d" % freq)
			if freq == current_module.current_speed:
				freq_option.selected = freq_option.get_item_count() - 1

func populate_command_rate():
	var cr_option = $BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/CommandRate/Value
	cr_option.clear()
	cr_option.add_item("1T")
	cr_option.add_item("2T")
	cr_option.selected = memory_controller.current_command_rate - 1

func populate_xmp_profiles():
	var xmp_option = $BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/XMPProfile/Value
	xmp_option.clear()
	xmp_option.add_item("Disabled")
	xmp_option.add_item("Profile 1: %d MHz %s" % [current_module.rated_speed, "-".join(current_module.rated_timings)])
	xmp_option.selected = 0

func setup_ui_values():
	# Set timing values
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/CLOption/Value.value = current_module.current_timings[0]
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/tRCDOption/Value.value = current_module.current_timings[1]
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/tRPOption/Value.value = current_module.current_timings[2]
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/tRASOption/Value.value = current_module.current_timings[3]
	
	# Set voltage values
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/DRAMVoltage/Value.value = current_module.current_voltage
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/VCCIOVoltage/Value.value = memory_controller.vccio_voltage
	$BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/VCCSAVoltage/Value.value = memory_controller.vccsa_voltage

func update_display():
	var info_text = $BIOSContainer/MainContent/RightPanel/InfoContainer/SystemInfo
	
	# Calculate temperature color
	var temp_color = "#00FF00"  # Green
	if current_module.temperature > 75:
		temp_color = "#FF0000"  # Red
	elif current_module.temperature > 65:
		temp_color = "#FFFF00"  # Yellow
	
	# Calculate stability color
	var stability_color = "#00FF00"  # Green
	if current_module.stability_score < 60:
		stability_color = "#FF0000"  # Red
	elif current_module.stability_score < 80:
		stability_color = "#FFFF00"  # Yellow
	
	info_text.text = "[b]System Information[/b]\n"
	info_text.text += "════════════════════════════════════\n"
	info_text.text += "Memory: %s\n" % current_module.name
	info_text.text += "IC Type: %s\n" % get_ic_name(current_module.ic_type)
	info_text.text += "Frequency: [color=#00FFFF]%d MHz[/color]\n" % current_module.current_speed
	info_text.text += "Timings: [color=#00FFFF]%s[/color]\n" % "-".join(current_module.current_timings)
	info_text.text += "Voltage: [color=#FFFF00]%.3fV[/color]\n\n" % current_module.current_voltage
	
	info_text.text += "[b]Temperature Monitor[/b]\n"
	info_text.text += "════════════════════════════════════\n"
	info_text.text += "DIMM Temperature: [color=%s]%.1f°C[/color]\n" % [temp_color, current_module.temperature]
	info_text.text += "System Temperature: [color=#00FF00]%.1f°C[/color]\n\n" % game_data.ambient_temperature
	
	info_text.text += "[b]Stability Status[/b]\n"
	info_text.text += "════════════════════════════════════\n"
	info_text.text += "Current Stability: [color=%s]%.1f%%[/color]\n" % [stability_color, current_module.stability_score]
	info_text.text += "Errors Detected: [color=#FF0000]%d[/color]" % current_module.errors

func get_ic_name(ic_type: GameData.MemoryIC) -> String:
	match ic_type:
		GameData.MemoryIC.SAMSUNG_BDIE: return "Samsung B-Die"
		GameData.MemoryIC.SAMSUNG_CDIE: return "Samsung C-Die"
		GameData.MemoryIC.SAMSUNG_EDIE: return "Samsung E-Die"
		GameData.MemoryIC.HYNIX_CJR: return "Hynix CJR"
		GameData.MemoryIC.HYNIX_DJR: return "Hynix DJR"
		GameData.MemoryIC.HYNIX_MFR: return "Hynix MFR"
		GameData.MemoryIC.MICRON_EDIE: return "Micron E-Die"
		GameData.MemoryIC.MICRON_BDIE: return "Micron B-Die"
		_: return "Unknown"

func _on_frequency_changed(index: int):
	var freq_text = $BIOSContainer/MainContent/LeftPanel/SettingsScroll/SettingsList/FrequencyOption/Value.get_item_text(index)
	var new_freq = int(freq_text.split("-")[1])
	
	var old_freq = current_module.current_speed
	current_module.current_speed = new_freq
	
	# Calculate stability impact
	var freq_stress = abs(new_freq - current_module.rated_speed) / float(current_module.rated_speed)
	var stability_penalty = min(50, freq_stress * 100)
	current_module.stability_score = max(10, 100 - stability_penalty)
	current_module.temperature += (new_freq - old_freq) * 0.01
	
	update_display()
	update_help_text("Frequency changed to %d MHz" % new_freq)

func _on_cl_changed(value: float):
	current_module.current_timings[0] = int(value)
	recalculate_stability()
	update_display()
	update_help_text("CAS Latency set to %d" % int(value))

func _on_trcd_changed(value: float):
	current_module.current_timings[1] = int(value)
	recalculate_stability()
	update_display()
	update_help_text("tRCD set to %d" % int(value))

func _on_trp_changed(value: float):
	current_module.current_timings[2] = int(value)
	recalculate_stability()
	update_display()
	update_help_text("tRP set to %d" % int(value))

func _on_tras_changed(value: float):
	current_module.current_timings[3] = int(value)
	recalculate_stability()
	update_display()
	update_help_text("tRAS set to %d" % int(value))

func _on_command_rate_changed(index: int):
	memory_controller.current_command_rate = index + 1
	update_display()
	update_help_text("Command Rate set to %dT" % (index + 1))

func _on_dram_voltage_changed(value: float):
	current_module.current_voltage = value
	
	# Higher voltage improves stability but increases temperature
	var voltage_benefit = (value - 1.2) * 20 if current_module.memory_type == GameData.MemoryType.DDR4 else (value - 1.1) * 25
	current_module.stability_score = min(100, current_module.stability_score + voltage_benefit)
	current_module.temperature += (value - 1.2) * 15 if current_module.memory_type == GameData.MemoryType.DDR4 else (value - 1.1) * 18
	
	update_display()
	update_help_text("DRAM Voltage set to %.3fV" % value)

func _on_vccio_voltage_changed(value: float):
	memory_controller.vccio_voltage = value
	update_display()
	update_help_text("VCCIO Voltage set to %.3fV" % value)

func _on_vccsa_voltage_changed(value: float):
	memory_controller.vccsa_voltage = value
	update_display()
	update_help_text("VCCSA Voltage set to %.3fV" % value)

func _on_xmp_profile_changed(index: int):
	if index == 1:  # Profile 1 selected
		current_module.current_speed = current_module.rated_speed
		current_module.current_timings = current_module.rated_timings.duplicate()
		current_module.current_voltage = current_module.voltage
		current_module.stability_score = 85
		
		# Update UI
		setup_ui_values()
		populate_frequency_options()
		update_display()
		update_help_text("OMP Profile loaded: %d MHz @ %s" % [current_module.rated_speed, "-".join(current_module.rated_timings)])
	else:
		update_help_text("OMP Profile disabled")

func recalculate_stability():
	# Recalculate stability based on timing tightness
	var timing_tightness = 0
	for i in range(4):
		if current_module.current_timings[i] < current_module.jedec_timings[i]:
			timing_tightness += (current_module.jedec_timings[i] - current_module.current_timings[i]) * 2
	
	current_module.stability_score = max(10, 100 - timing_tightness)

func update_help_text(message: String):
	var help_text = $BIOSContainer/MainContent/RightPanel/InfoContainer/HelpText
	var help_content = "[b]Navigation Help[/b]\n"
	help_content += "════════════════════════════════════\n"
	help_content += "↑↓ : Select Item\n"
	help_content += "←→ : Change Value\n"
	help_content += "Enter : Enter Sub-menu\n"
	help_content += "ESC : Exit/Back\n"
	help_content += "F10 : Save & Exit\n"
	help_content += "F5 : Load Optimized Defaults\n"
	help_content += "F6 : Load OMP Profile\n"
	help_content += "F7 : Run Stability Test\n\n"
	help_content += "[b]Current Selection[/b]\n"
	help_content += "════════════════════════════════════\n"
	help_content += message
	
	help_text.text = help_content

func _on_exit_button_pressed():
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _on_focus_changed(control: Control):
	if control != null:
		var help_messages = {
			"FrequencyOption": "Adjust memory frequency for overclocking",
			"CLOption": "CAS Latency - Lower is better but harder to achieve",
			"tRCDOption": "RAS to CAS Delay - Time between row activation and column access",
			"tRPOption": "RAS Precharge - Time to close a row before opening another",
			"tRASOption": "Row Active Time - Minimum time a row must stay open",
			"CommandRate": "1T has better performance, 2T has better stability",
			"DRAMVoltage": "Higher voltage improves stability but increases heat",
			"VCCIOVoltage": "Memory controller I/O voltage",
			"VCCSAVoltage": "System Agent voltage - helps with high frequency",
			"XMPProfile": "Load manufacturer's tested overclock profile"
		}
		
		for key in help_messages:
			if control.get_path().to_string().contains(key):
				update_help_text(help_messages[key])
				break

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		_on_exit_button_pressed()
	elif event is InputEventKey and event.pressed:
		match event.keycode:
			KEY_F5:
				# Load optimized defaults (JEDEC)
				current_module.current_speed = current_module.jedec_speed
				current_module.current_timings = current_module.jedec_timings.duplicate()
				current_module.current_voltage = 1.2 if current_module.memory_type == GameData.MemoryType.DDR4 else 1.1
				current_module.stability_score = 100
				current_module.temperature = game_data.ambient_temperature + 10
				setup_ui_values()
				populate_frequency_options()
				update_display()
				update_help_text("Loaded optimized defaults (JEDEC)")
			KEY_F6:
				# Load OMP
				_on_xmp_profile_changed(1)
			KEY_F7:
				# Run stress test
				run_stress_test()
			KEY_F10:
				# Save and exit
				update_help_text("Settings saved! Returning to main menu...")
				await get_tree().create_timer(1.0).timeout
				_on_exit_button_pressed()

func run_stress_test():
	update_help_text("Running stability test...")
	
	# Simple stress test simulation
	if current_module.stability_score > 80:
		update_help_text("✓ STABLE - No errors detected!")
	elif current_module.stability_score > 60:
		current_module.errors += randi() % 5 + 1
		update_help_text("⚠ UNSTABLE - %d errors detected" % current_module.errors)
	else:
		current_module.errors += randi() % 20 + 5
		update_help_text("✗ FAILED - System would crash!")
	
	update_display()
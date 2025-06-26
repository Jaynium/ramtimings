extends Control

# Simulated game state (in real implementation, would load from singleton)
var current_module: GameData.MemoryModule
var memory_controller: GameData.MemoryController
var game_data: GameData

func _ready():
	game_data = GameData.new()
	# Initialize with test data for now
	setup_test_data()
	update_display()

func setup_test_data():
	# Create a test module
	current_module = GameData.MemoryModule.new(
		"G.Skill Trident Z Neo 3600",
		GameData.MemoryType.DDR4,
		GameData.MemoryIC.SAMSUNG_CDIE,
		2133, [15, 15, 15, 36],
		3600, [16, 19, 19, 39],
		1.35, 16, 38.0, 7
	)
	
	# Create test controller
	memory_controller = GameData.MemoryController.new(7, 1.5, true, true, 2, 1, 1.1, 1.25)
	
	# Set initial values in UI
	setup_ui_values()

func setup_ui_values():
	# Frequency
	var freq_slider = $MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Frequency/FreqSlider
	freq_slider.value = current_module.current_speed
	
	# Timings
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/CLContainer/CLSpinBox.value = current_module.current_timings[0]
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/tRCDContainer/tRCDSpinBox.value = current_module.current_timings[1]
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/tRPContainer/tRPSpinBox.value = current_module.current_timings[2]
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/tRASContainer/tRASSpinBox.value = current_module.current_timings[3]
	
	# Voltages
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Voltage/DRAMContainer/DRAMSpinBox.value = current_module.current_voltage
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Voltage/VCCIOContainer/VCCIOSpinBox.value = memory_controller.vccio_voltage
	$MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Voltage/VCCSAContainer/VCCSASpinBox.value = memory_controller.vccsa_voltage

func update_display():
	# Update RAM info
	var ram_info = $MainContainer/LeftPanel/LeftMargin/StatusDisplay/RAMInfo
	ram_info.text = "[b]RAM:[/b] %s\n[b]Frequency:[/b] %d MHz\n[b]Timings:[/b] %s\n[b]Voltage:[/b] %.3fV" % [
		current_module.name,
		current_module.current_speed,
		"-".join(current_module.current_timings),
		current_module.current_voltage
	]
	
	# Update temperature info
	var temp_info = $MainContainer/LeftPanel/LeftMargin/StatusDisplay/TempInfo
	var temp_color = "white"
	if current_module.temperature > 75:
		temp_color = "red"
	elif current_module.temperature > 65:
		temp_color = "yellow"
	else:
		temp_color = "green"
		
	temp_info.text = "[b]Temperature:[/b] [color=%s]%.1f°C[/color]\n[b]Stability:[/b] %.1f%%\n[b]Errors:[/b] %d" % [
		temp_color,
		current_module.temperature,
		current_module.stability_score,
		current_module.errors
	]
	
	# Update IMC info
	var imc_info = $MainContainer/LeftPanel/LeftMargin/StatusDisplay/IMCInfo
	imc_info.text = "[b]IMC Quality:[/b] %d/10\n[b]Command Rate:[/b] %dT\n[b]VCCIO:[/b] %.3fV\n[b]VCCSA:[/b] %.3fV" % [
		memory_controller.imc_quality,
		memory_controller.current_command_rate,
		memory_controller.vccio_voltage,
		memory_controller.vccsa_voltage
	]

func _on_freq_slider_value_changed(value: float):
	var freq_label = $MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Frequency/FreqValue
	freq_label.text = "%d MHz" % int(value)

func _on_apply_freq_button_pressed():
	var new_freq = int($MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Frequency/FreqSlider.value)
	
	# Update module frequency
	var old_freq = current_module.current_speed
	current_module.current_speed = new_freq
	
	# Calculate stability impact
	var freq_stress = abs(new_freq - current_module.rated_speed) / float(current_module.rated_speed)
	var stability_penalty = min(50, freq_stress * 100)
	current_module.stability_score = max(10, 100 - stability_penalty)
	
	# Temperature increases with frequency
	current_module.temperature += (new_freq - old_freq) * 0.01
	
	update_display()
	show_notification("Frequency set to %d MHz" % new_freq)

func _on_apply_timings_button_pressed():
	# Get new timings
	var new_timings = [
		int($MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/CLContainer/CLSpinBox.value),
		int($MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/tRCDContainer/tRCDSpinBox.value),
		int($MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/tRPContainer/tRPSpinBox.value),
		int($MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Timings/tRASContainer/tRASSpinBox.value)
	]
	
	current_module.current_timings = new_timings
	
	# Tighter timings reduce stability
	var timing_tightness = 0
	for i in range(4):
		if new_timings[i] < current_module.jedec_timings[i]:
			timing_tightness += (current_module.jedec_timings[i] - new_timings[i]) * 2
	
	current_module.stability_score = max(10, current_module.stability_score - timing_tightness)
	
	update_display()
	show_notification("Timings updated to %s" % "-".join(new_timings))

func _on_apply_voltage_button_pressed():
	# Get new voltages
	var new_dram_voltage = $MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Voltage/DRAMContainer/DRAMSpinBox.value
	var new_vccio = $MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Voltage/VCCIOContainer/VCCIOSpinBox.value
	var new_vccsa = $MainContainer/RightPanel/RightMargin/VBoxContainer/TabContainer/Voltage/VCCSAContainer/VCCSASpinBox.value
	
	# Update voltages
	current_module.current_voltage = new_dram_voltage
	memory_controller.vccio_voltage = new_vccio
	memory_controller.vccsa_voltage = new_vccsa
	
	# Higher voltage improves stability but increases temperature
	var voltage_benefit = (new_dram_voltage - 1.2) * 20 if current_module.memory_type == GameData.MemoryType.DDR4 else (new_dram_voltage - 1.1) * 25
	current_module.stability_score = min(100, current_module.stability_score + voltage_benefit)
	current_module.temperature += (new_dram_voltage - 1.2) * 15 if current_module.memory_type == GameData.MemoryType.DDR4 else (new_dram_voltage - 1.1) * 18
	
	update_display()
	show_notification("Voltages updated")

func _on_apply_xmp_button_pressed():
	# Apply XMP/DOCP profile
	current_module.current_speed = current_module.rated_speed
	current_module.current_timings = current_module.rated_timings.duplicate()
	current_module.current_voltage = current_module.voltage
	current_module.stability_score = 85  # XMP profiles are usually stable
	
	# Update UI
	setup_ui_values()
	update_display()
	show_notification("XMP Profile Applied: %d MHz @ %s" % [current_module.rated_speed, "-".join(current_module.rated_timings)])

func _on_reset_button_pressed():
	# Reset to JEDEC standards
	current_module.current_speed = current_module.jedec_speed
	current_module.current_timings = current_module.jedec_timings.duplicate()
	current_module.current_voltage = 1.2 if current_module.memory_type == GameData.MemoryType.DDR4 else 1.1
	current_module.stability_score = 100
	current_module.temperature = game_data.ambient_temperature + 10
	
	# Update UI
	setup_ui_values()
	update_display()
	show_notification("Reset to JEDEC defaults")

func _on_stress_test_button_pressed():
	# Simple stress test simulation
	show_notification("Running stress test...")
	
	# Simulate test results based on stability score
	if current_module.stability_score > 80:
		show_notification("✓ STABLE - No errors detected!")
	elif current_module.stability_score > 60:
		current_module.errors += randi() % 5 + 1
		show_notification("⚠ UNSTABLE - %d errors detected" % current_module.errors)
	else:
		current_module.errors += randi() % 20 + 5
		show_notification("✗ FAILED - System would crash!")
	
	update_display()

func _on_back_button_pressed():
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func show_notification(text: String):
	# Simple notification system
	var label = Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 18)
	label.modulate = Color(1, 1, 0)
	
	var container = $MainContainer/RightPanel/RightMargin/VBoxContainer
	container.add_child(label)
	
	# Fade out and remove after 3 seconds
	var tween = create_tween()
	tween.tween_interval(2.0)
	tween.tween_property(label, "modulate:a", 0.0, 1.0)
	tween.tween_callback(label.queue_free)
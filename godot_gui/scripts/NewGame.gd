extends Control

var selected_experience_level: int = 0
var selected_ram_kit: GameData.MemoryModule = null
var selected_controller: GameData.MemoryController = null

func _ready():
	populate_ram_kits()
	populate_controllers()

func populate_ram_kits():
	var ram_list = $MarginContainer/VBoxContainer/RAMSelection/ScrollContainer/RAMList
	var kits = GameData.new().get_available_ram_kits()
	
	# Clear existing items
	for child in ram_list.get_children():
		child.queue_free()
	
	# Group kits by type
	var ddr4_label = Label.new()
	ddr4_label.text = "=== DDR4 Kits ==="
	ddr4_label.add_theme_font_size_override("font_size", 20)
	ram_list.add_child(ddr4_label)
	
	# Add DDR4 kits
	for kit in kits:
		if kit.memory_type == GameData.MemoryType.DDR4:
			add_ram_kit_button(kit, ram_list)
	
	# DDR5 separator
	var ddr5_label = Label.new()
	ddr5_label.text = "\n=== DDR5 Kits ==="
	ddr5_label.add_theme_font_size_override("font_size", 20)
	ram_list.add_child(ddr5_label)
	
	# Add DDR5 kits
	for kit in kits:
		if kit.memory_type == GameData.MemoryType.DDR5:
			add_ram_kit_button(kit, ram_list)

func add_ram_kit_button(kit: GameData.MemoryModule, parent: Node):
	var button = Button.new()
	button.text = "%s\n  IC: %s | JEDEC: %d MHz | Rated: %d MHz | %dGB x2 | Quality: %d/10" % [
		kit.name,
		get_ic_name(kit.ic_type),
		kit.jedec_speed,
		kit.rated_speed,
		kit.capacity,
		kit.quality_bin
	]
	button.add_theme_font_size_override("font_size", 16)
	button.toggle_mode = true
	button.pressed.connect(_on_ram_kit_selected.bind(kit, button))
	parent.add_child(button)

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

func populate_controllers():
	var controller_options = $MarginContainer/VBoxContainer/ControllerSection/ControllerOptions
	var controllers = GameData.new().get_available_controllers()
	
	controller_options.clear()
	for controller in controllers:
		controller_options.add_item("%s (Quality: %d/10)" % [controller.name, controller.controller.imc_quality])

func _on_name_input_text_changed(new_text: String):
	check_can_start()

func _on_experience_selected(level: int):
	selected_experience_level = level
	check_can_start()

func _on_ram_kit_selected(kit: GameData.MemoryModule, button: Button):
	# Unselect all other buttons
	var ram_list = $MarginContainer/VBoxContainer/RAMSelection/ScrollContainer/RAMList
	for child in ram_list.get_children():
		if child is Button and child != button:
			child.button_pressed = false
	
	selected_ram_kit = kit
	check_can_start()

func _on_controller_selected(index: int):
	var controllers = GameData.new().get_available_controllers()
	if index >= 0 and index < controllers.size():
		selected_controller = controllers[index].controller
	check_can_start()

func check_can_start():
	var start_button = $MarginContainer/VBoxContainer/ButtonContainer/StartButton
	var name_input = $MarginContainer/VBoxContainer/NameSection/NameInput
	
	start_button.disabled = not (
		name_input.text.length() > 0 and
		selected_experience_level > 0 and
		selected_ram_kit != null and
		selected_controller != null
	)

func _on_back_button_pressed():
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _on_start_button_pressed():
	# Save game state
	var game_data = GameData.new()
	game_data.player_name = $MarginContainer/VBoxContainer/NameSection/NameInput.text
	game_data.experience_level = selected_experience_level
	game_data.current_modules = [selected_ram_kit, selected_ram_kit]  # Dual channel
	game_data.memory_controller = selected_controller
	
	# TODO: Save to singleton or file
	
	# Transition to overclocking lab
	get_tree().change_scene_to_file("res://scenes/OverclockingLab.tscn")
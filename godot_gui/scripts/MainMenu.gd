extends Control

# Main menu controller script

func _ready():
	# Center the window on screen startup
	get_window().position = DisplayServer.screen_get_position() + (DisplayServer.screen_get_size() - get_window().size) / 2

func _on_new_game_button_pressed():
	# Transition to RAM selection scene
	get_tree().change_scene_to_file("res://scenes/NewGame.tscn")

func _on_load_game_button_pressed():
	# TODO: Implement save/load system
	print("Load game functionality not yet implemented")

func _on_knowledge_base_button_pressed():
	# Transition to knowledge base scene
	get_tree().change_scene_to_file("res://scenes/KnowledgeBase.tscn")

func _on_settings_button_pressed():
	# TODO: Implement settings menu
	print("Settings menu not yet implemented")

func _on_exit_button_pressed():
	get_tree().quit()
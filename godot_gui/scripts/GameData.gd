extends Node
# Singleton for game data management

class_name GameData

# Enums for memory types and ICs
enum MemoryType { DDR4, DDR5 }
enum MemoryIC {
	SAMSUNG_BDIE,
	SAMSUNG_CDIE,
	SAMSUNG_EDIE,
	HYNIX_CJR,
	HYNIX_DJR,
	HYNIX_MFR,
	MICRON_EDIE,
	MICRON_BDIE
}

# Memory module class
class MemoryModule:
	var name: String
	var memory_type: MemoryType
	var ic_type: MemoryIC
	var jedec_speed: int
	var jedec_timings: Array[int]  # [CL, tRCD, tRP, tRAS]
	var rated_speed: int
	var rated_timings: Array[int]
	var voltage: float
	var capacity: int  # GB per stick
	var temperature: float
	var quality_bin: int  # 1-10
	
	# Current settings
	var current_speed: int
	var current_timings: Array[int]
	var current_voltage: float
	var stability_score: float = 100.0
	var errors: int = 0
	
	func _init(p_name: String, p_type: MemoryType, p_ic: MemoryIC, p_jedec_speed: int, 
			p_jedec_timings: Array, p_rated_speed: int, p_rated_timings: Array, 
			p_voltage: float, p_capacity: int, p_temp: float, p_quality: int):
		name = p_name
		memory_type = p_type
		ic_type = p_ic
		jedec_speed = p_jedec_speed
		jedec_timings = p_jedec_timings
		rated_speed = p_rated_speed
		rated_timings = p_rated_timings
		voltage = p_voltage
		capacity = p_capacity
		temperature = p_temp
		quality_bin = p_quality
		
		# Initialize current settings to JEDEC
		current_speed = jedec_speed
		current_timings = jedec_timings.duplicate()
		current_voltage = 1.2 if memory_type == MemoryType.DDR4 else 1.1

# Memory controller class
class MemoryController:
	var imc_quality: int  # 1-10
	var max_safe_voltage: float
	var supports_gear_down: bool
	var supports_command_rate_1t: bool
	var current_command_rate: int = 2  # 1T or 2T
	var current_gear_mode: int = 1  # 1 or 2
	var vccio_voltage: float
	var vccsa_voltage: float
	
	func _init(p_quality: int, p_max_voltage: float, p_gear_down: bool, p_cr_1t: bool,
			p_cr: int, p_gear: int, p_vccio: float, p_vccsa: float):
		imc_quality = p_quality
		max_safe_voltage = p_max_voltage
		supports_gear_down = p_gear_down
		supports_command_rate_1t = p_cr_1t
		current_command_rate = p_cr
		current_gear_mode = p_gear
		vccio_voltage = p_vccio
		vccsa_voltage = p_vccsa

# Game state variables
var player_name: String = ""
var experience_level: int = 0
var achievements: Array = []
var current_modules: Array[MemoryModule] = []
var memory_controller: MemoryController = null
var ambient_temperature: float = 25.0
var cooling_solution: String = "Stock"

# Available RAM kits
func get_available_ram_kits() -> Array[MemoryModule]:
	var kits: Array[MemoryModule] = []
	
	# DDR4 Kits
	kits.append(MemoryModule.new("Pirate Revenge LPX 3200", MemoryType.DDR4, MemoryIC.HYNIX_CJR,
		2133, [15, 15, 15, 36], 3200, [16, 18, 18, 36], 1.35, 16, 35.0, 6))
	kits.append(MemoryModule.new("GameSkill Blade Z Neo 3600", MemoryType.DDR4, MemoryIC.SAMSUNG_CDIE,
		2133, [15, 15, 15, 36], 3600, [16, 19, 19, 39], 1.35, 16, 38.0, 7))
	kits.append(MemoryModule.new("GameSkill Blade Z Elite 4000", MemoryType.DDR4, MemoryIC.SAMSUNG_BDIE,
		2133, [15, 15, 15, 36], 4000, [19, 19, 19, 39], 1.4, 16, 40.0, 9))
	kits.append(MemoryModule.new("Essential Tactical 3200", MemoryType.DDR4, MemoryIC.MICRON_EDIE,
		2133, [15, 15, 15, 36], 3200, [16, 18, 18, 36], 1.35, 16, 36.0, 7))
	kits.append(MemoryModule.new("Squad Power Xtreme 4500", MemoryType.DDR4, MemoryIC.SAMSUNG_BDIE,
		2133, [15, 15, 15, 36], 4500, [19, 19, 19, 39], 1.45, 16, 42.0, 10))
	kits.append(MemoryModule.new("Royal Rage Monster 3600", MemoryType.DDR4, MemoryIC.HYNIX_DJR,
		2133, [15, 15, 15, 36], 3600, [18, 22, 22, 42], 1.35, 16, 37.0, 6))
	kits.append(MemoryModule.new("Freedom Snake Steel 4400", MemoryType.DDR4, MemoryIC.SAMSUNG_BDIE,
		2133, [15, 15, 15, 36], 4400, [19, 19, 19, 39], 1.45, 16, 41.0, 9))
	kits.append(MemoryModule.new("Pirate Revenge RGB Pro 3600", MemoryType.DDR4, MemoryIC.SAMSUNG_CDIE,
		2133, [15, 15, 15, 36], 3600, [18, 22, 22, 42], 1.35, 16, 38.0, 7))
	kits.append(MemoryModule.new("Alpha Prime Matrix D60G 3600", MemoryType.DDR4, MemoryIC.HYNIX_CJR,
		2133, [15, 15, 15, 36], 3600, [18, 20, 20, 40], 1.35, 16, 38.0, 6))
	kits.append(MemoryModule.new("HeatMax STRONGRAM RGB 3200", MemoryType.DDR4, MemoryIC.SAMSUNG_CDIE,
		2133, [15, 15, 15, 36], 3200, [16, 18, 18, 36], 1.35, 16, 36.0, 6))
	
	# DDR5 Kits
	kits.append(MemoryModule.new("Pirate Supreme Platinum 5200", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
		4800, [40, 40, 40, 76], 5200, [40, 40, 40, 76], 1.25, 32, 42.0, 8))
	kits.append(MemoryModule.new("GameSkill Blade Z5 RGB 6000", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
		4800, [40, 40, 40, 76], 6000, [30, 38, 38, 96], 1.35, 32, 45.0, 9))
	kits.append(MemoryModule.new("Royal Rage Monster 5600", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
		4800, [40, 40, 40, 76], 5600, [36, 36, 36, 76], 1.25, 32, 43.0, 7))
	kits.append(MemoryModule.new("Pirate Revenge DDR5 5600", MemoryType.DDR5, MemoryIC.HYNIX_MFR,
		4800, [40, 40, 40, 76], 5600, [36, 36, 36, 76], 1.25, 32, 43.0, 7))
	kits.append(MemoryModule.new("Squad Power Delta RGB 6200", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
		4800, [40, 40, 40, 76], 6200, [36, 36, 36, 76], 1.35, 32, 46.0, 8))
	kits.append(MemoryModule.new("Alpha Prime Spear RGB 6000", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
		4800, [40, 40, 40, 76], 6000, [32, 38, 38, 96], 1.35, 32, 45.0, 8))
	kits.append(MemoryModule.new("Essential DDR5 5200", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
		4800, [40, 40, 40, 76], 5200, [42, 42, 42, 84], 1.1, 32, 40.0, 6))
	kits.append(MemoryModule.new("Freedom Snake Poison DDR5 6200", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
		4800, [40, 40, 40, 76], 6200, [36, 36, 36, 76], 1.35, 32, 46.0, 9))
	kits.append(MemoryModule.new("HeatMax STRONGRAM RC DDR5 5600", MemoryType.DDR5, MemoryIC.HYNIX_MFR,
		4800, [40, 40, 40, 76], 5600, [36, 36, 36, 76], 1.25, 32, 43.0, 7))
	kits.append(MemoryModule.new("GameSkill Blade Z5 Elite 6400", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
		4800, [40, 40, 40, 76], 6400, [32, 39, 39, 102], 1.4, 32, 48.0, 10))
	
	return kits

# Available memory controllers
func get_available_controllers() -> Array:
	return [
		{"name": "Blue Chip Z690/Z790 IMC", "controller": MemoryController.new(7, 1.5, true, true, 2, 1, 1.1, 1.25)},
		{"name": "Red Stone Zen 3 IMC", "controller": MemoryController.new(6, 1.45, false, false, 1, 1, 0.9, 1.0)},
		{"name": "Blue Chip Z490/Z590 IMC", "controller": MemoryController.new(8, 1.55, true, true, 2, 1, 1.15, 1.3)},
		{"name": "Red Stone Zen 4 IMC", "controller": MemoryController.new(8, 1.4, true, true, 1, 1, 0.95, 1.05)}
	]

# IC characteristics for overclocking
func get_ic_characteristics(ic_type: MemoryIC) -> Dictionary:
	match ic_type:
		MemoryIC.SAMSUNG_BDIE:
			return {
				"min_freq": 3200, "max_freq": 4400,
				"voltage_scaling": "excellent",
				"temp_sensitivity": "moderate",
				"tight_timings": true
			}
		MemoryIC.SAMSUNG_CDIE:
			return {
				"min_freq": 3000, "max_freq": 3800,
				"voltage_scaling": "limited",
				"temp_sensitivity": "high",
				"tight_timings": false
			}
		MemoryIC.SAMSUNG_EDIE:
			return {
				"min_freq": 2800, "max_freq": 3400,
				"voltage_scaling": "moderate",
				"temp_sensitivity": "moderate",
				"tight_timings": false
			}
		MemoryIC.HYNIX_CJR:
			return {
				"min_freq": 3000, "max_freq": 3600,
				"voltage_scaling": "moderate",
				"temp_sensitivity": "low",
				"tight_timings": false
			}
		MemoryIC.HYNIX_DJR:
			return {
				"min_freq": 3200, "max_freq": 3800,
				"voltage_scaling": "moderate",
				"temp_sensitivity": "low",
				"tight_timings": false
			}
		MemoryIC.HYNIX_MFR:
			return {
				"min_freq": 2400, "max_freq": 3000,
				"voltage_scaling": "poor",
				"temp_sensitivity": "high",
				"tight_timings": false
			}
		MemoryIC.MICRON_EDIE:
			return {
				"min_freq": 3000, "max_freq": 3600,
				"voltage_scaling": "moderate",
				"temp_sensitivity": "high",
				"tight_timings": false
			}
		MemoryIC.MICRON_BDIE:
			return {
				"min_freq": 3400, "max_freq": 4000,
				"voltage_scaling": "good",
				"temp_sensitivity": "moderate",
				"tight_timings": true
			}
		_:
			return {}
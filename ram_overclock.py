#!/usr/bin/env python3
"""
RAM Overclocking Simulator
A detailed educational game that simulates the complexities of memory overclocking
Based on real-world principles used by experts like Buildzoid
"""

import os
import sys
import time
import random
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class MemoryType(Enum):
    DDR4 = "DDR4"
    DDR5 = "DDR5"

class MemoryIC(Enum):
    SAMSUNG_BDIE = "Samsung B-Die"
    SAMSUNG_CDIE = "Samsung C-Die" 
    SAMSUNG_EDIE = "Samsung E-Die"
    HYNIX_CJR = "Hynix CJR"
    HYNIX_DJR = "Hynix DJR"
    HYNIX_MFR = "Hynix MFR"
    MICRON_EDIE = "Micron E-Die"
    MICRON_BDIE = "Micron B-Die"

@dataclass
class MemoryModule:
    name: str
    memory_type: MemoryType
    ic_type: MemoryIC
    jedec_speed: int
    jedec_timings: Tuple[int, int, int, int]  # CL, tRCD, tRP, tRAS
    rated_speed: int
    rated_timings: Tuple[int, int, int, int]
    voltage: float
    capacity: int  # GB per stick
    temperature: float
    quality_bin: int  # 1-10, affects overclocking potential
    
    def __post_init__(self):
        self.current_speed = self.jedec_speed
        self.current_timings = list(self.jedec_timings)
        self.current_voltage = 1.2 if self.memory_type == MemoryType.DDR4 else 1.1
        self.stability_score = 100
        self.errors = 0

@dataclass
class MemoryController:
    imc_quality: int  # 1-10, affects max stable frequency
    max_safe_voltage: float
    supports_gear_down: bool
    supports_command_rate_1t: bool
    current_command_rate: int  # 1T or 2T
    current_gear_mode: int  # 1 or 2 (DDR5 only)
    vccio_voltage: float
    vccsa_voltage: float

class RAMOverclockGame:
    def __init__(self):
        self.player_name = ""
        self.experience_level = 0
        self.achievements = []
        self.current_modules: List[MemoryModule] = []
        self.memory_controller = None
        self.ambient_temperature = 25.0
        self.cooling_solution = "Stock"
        self.stress_test_running = False
        self.game_data = self.load_game_data()
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_banner(self):
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                   RAM OVERCLOCKING SIMULATOR                 ║")
        print("║              Learn Real Memory Overclocking!                ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
    def main_menu(self):
        while True:
            self.clear_screen()
            self.print_banner()
            
            if self.player_name:
                print(f"Welcome back, {self.player_name}! (Level {self.experience_level})")
                print()
            
            print("1. Start New Game")
            print("2. Load Game")
            print("3. Memory Overview")
            print("4. Overclocking Lab")
            print("5. Stress Testing")
            print("6. Temperature Monitor")
            print("7. Knowledge Base")
            print("8. Achievements")
            print("9. Settings")
            print("0. Exit")
            print()
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                self.new_game()
            elif choice == "2":
                self.load_game()
            elif choice == "3" and self.current_modules:
                self.memory_overview()
            elif choice == "4" and self.current_modules:
                self.overclocking_lab()
            elif choice == "5" and self.current_modules:
                self.stress_testing_menu()
            elif choice == "6" and self.current_modules:
                self.temperature_monitor()
            elif choice == "7":
                self.knowledge_base()
            elif choice == "8":
                self.show_achievements()
            elif choice == "9":
                self.settings_menu()
            elif choice == "0":
                print("Thanks for playing!")
                sys.exit(0)
            else:
                print("Invalid option or no memory installed!")
                input("Press Enter to continue...")
                
    def new_game(self):
        self.clear_screen()
        self.print_banner()
        
        print("Starting new game...")
        print()
        
        self.player_name = input("Enter your overclocker name: ").strip()
        if not self.player_name:
            self.player_name = "Anonymous OC'er"
            
        print()
        print("Choose your experience level:")
        print("1. Beginner (Safe settings, guided experience)")
        print("2. Intermediate (Some freedom, moderate risk)")
        print("3. Expert (Full control, high risk/reward)")
        
        level_choice = input("Select level (1-3): ").strip()
        self.experience_level = max(1, min(3, int(level_choice) if level_choice.isdigit() else 1))
        
        print()
        print("Choose your starting memory kit:")
        self.choose_memory_kit()
        
        print()
        print("Choose your memory controller:")
        self.choose_memory_controller()
        
        self.save_game()
        print(f"\nWelcome to RAM overclocking, {self.player_name}!")
        input("Press Enter to continue...")
        
    def choose_memory_kit(self):
        kits = [
            # DDR4 Kits
            MemoryModule("Corsair Vengeance LPX 3200", MemoryType.DDR4, MemoryIC.HYNIX_CJR, 
                        2133, (15, 15, 15, 36), 3200, (16, 18, 18, 36), 1.35, 16, 35.0, 6),
            MemoryModule("G.Skill Trident Z Neo 3600", MemoryType.DDR4, MemoryIC.SAMSUNG_CDIE,
                        2133, (15, 15, 15, 36), 3600, (16, 19, 19, 39), 1.35, 16, 38.0, 7),
            MemoryModule("G.Skill Trident Z Royal 4000", MemoryType.DDR4, MemoryIC.SAMSUNG_BDIE,
                        2133, (15, 15, 15, 36), 4000, (19, 19, 19, 39), 1.4, 16, 40.0, 9),
            MemoryModule("Crucial Ballistix 3200", MemoryType.DDR4, MemoryIC.MICRON_EDIE,
                        2133, (15, 15, 15, 36), 3200, (16, 18, 18, 36), 1.35, 16, 36.0, 7),
            MemoryModule("Team T-Force Xtreem 4500", MemoryType.DDR4, MemoryIC.SAMSUNG_BDIE,
                        2133, (15, 15, 15, 36), 4500, (19, 19, 19, 39), 1.45, 16, 42.0, 10),
            MemoryModule("Kingston Fury Beast 3600", MemoryType.DDR4, MemoryIC.HYNIX_DJR,
                        2133, (15, 15, 15, 36), 3600, (18, 22, 22, 42), 1.35, 16, 37.0, 6),
            MemoryModule("Patriot Viper Steel 4400", MemoryType.DDR4, MemoryIC.SAMSUNG_BDIE,
                        2133, (15, 15, 15, 36), 4400, (19, 19, 19, 39), 1.45, 16, 41.0, 9),
            MemoryModule("Corsair Vengeance RGB Pro 3600", MemoryType.DDR4, MemoryIC.SAMSUNG_CDIE,
                        2133, (15, 15, 15, 36), 3600, (18, 22, 22, 42), 1.35, 16, 38.0, 7),
            MemoryModule("ADATA XPG Spectrix D60G 3600", MemoryType.DDR4, MemoryIC.HYNIX_CJR,
                        2133, (15, 15, 15, 36), 3600, (18, 20, 20, 40), 1.35, 16, 38.0, 6),
            MemoryModule("Thermaltake TOUGHRAM RGB 3200", MemoryType.DDR4, MemoryIC.SAMSUNG_CDIE,
                        2133, (15, 15, 15, 36), 3200, (16, 18, 18, 36), 1.35, 16, 36.0, 6),
            # DDR5 Kits
            MemoryModule("Corsair Dominator Platinum 5200", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
                        4800, (40, 40, 40, 76), 5200, (40, 40, 40, 76), 1.25, 32, 42.0, 8),
            MemoryModule("G.Skill Trident Z5 RGB 6000", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
                        4800, (40, 40, 40, 76), 6000, (30, 38, 38, 96), 1.35, 32, 45.0, 9),
            MemoryModule("Kingston Fury Beast 5600", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
                        4800, (40, 40, 40, 76), 5600, (36, 36, 36, 76), 1.25, 32, 43.0, 7),
            MemoryModule("Corsair Vengeance DDR5 5600", MemoryType.DDR5, MemoryIC.HYNIX_MFR,
                        4800, (40, 40, 40, 76), 5600, (36, 36, 36, 76), 1.25, 32, 43.0, 7),
            MemoryModule("TeamGroup T-Force Delta RGB 6200", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
                        4800, (40, 40, 40, 76), 6200, (36, 36, 36, 76), 1.35, 32, 46.0, 8),
            MemoryModule("ADATA XPG Lancer RGB 6000", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
                        4800, (40, 40, 40, 76), 6000, (32, 38, 38, 96), 1.35, 32, 45.0, 8),
            MemoryModule("Crucial DDR5 5200", MemoryType.DDR5, MemoryIC.MICRON_BDIE,
                        4800, (40, 40, 40, 76), 5200, (42, 42, 42, 84), 1.1, 32, 40.0, 6),
            MemoryModule("Patriot Viper Venom DDR5 6200", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
                        4800, (40, 40, 40, 76), 6200, (36, 36, 36, 76), 1.35, 32, 46.0, 9),
            MemoryModule("Thermaltake TOUGHRAM RC DDR5 5600", MemoryType.DDR5, MemoryIC.HYNIX_MFR,
                        4800, (40, 40, 40, 76), 5600, (36, 36, 36, 76), 1.25, 32, 43.0, 7),
            MemoryModule("G.Skill Trident Z5 Royal 6400", MemoryType.DDR5, MemoryIC.SAMSUNG_EDIE,
                        4800, (40, 40, 40, 76), 6400, (32, 39, 39, 102), 1.4, 32, 48.0, 10),
        ]
        
        print("Available memory kits:")
        print("\nDDR4 Kits:")
        ddr4_count = 0
        for i, kit in enumerate(kits, 1):
            if kit.memory_type == MemoryType.DDR4:
                ddr4_count += 1
                print(f"{i}. {kit.name}")
                print(f"   Type: {kit.memory_type.value}, IC: {kit.ic_type.value}")
                print(f"   JEDEC: {kit.jedec_speed} MHz, Rated: {kit.rated_speed} MHz")
                print(f"   Capacity: {kit.capacity}GB x2, Quality: {kit.quality_bin}/10")
                print()
        
        print("\nDDR5 Kits:")
        for i, kit in enumerate(kits, 1):
            if kit.memory_type == MemoryType.DDR5:
                print(f"{i}. {kit.name}")
                print(f"   Type: {kit.memory_type.value}, IC: {kit.ic_type.value}")
                print(f"   JEDEC: {kit.jedec_speed} MHz, Rated: {kit.rated_speed} MHz")
                print(f"   Capacity: {kit.capacity}GB x2, Quality: {kit.quality_bin}/10")
                print()
            
        choice = input(f"Select kit (1-{len(kits)}): ").strip()
        kit_index = max(0, min(len(kits)-1, int(choice) - 1 if choice.isdigit() else 0))
        
        selected_kit = kits[kit_index]
        self.current_modules = [selected_kit, selected_kit]  # Dual channel
        print(f"Selected: {selected_kit.name}")
        
    def choose_memory_controller(self):
        controllers = [
            ("Intel Z690/Z790 IMC", MemoryController(7, 1.5, True, True, 2, 1, 1.1, 1.25)),
            ("AMD Zen 3 IMC", MemoryController(6, 1.45, False, False, 1, 1, 0.9, 1.0)),
            ("Intel Z490/Z590 IMC", MemoryController(8, 1.55, True, True, 2, 1, 1.15, 1.3)),
            ("AMD Zen 4 IMC", MemoryController(8, 1.4, True, True, 1, 1, 0.95, 1.05)),
        ]
        
        print("Available memory controllers:")
        for i, (name, controller) in enumerate(controllers, 1):
            print(f"{i}. {name} (Quality: {controller.imc_quality}/10)")
            
        choice = input("Select controller (1-4): ").strip()
        controller_index = max(0, min(3, int(choice) - 1 if choice.isdigit() else 0))
        
        self.memory_controller = controllers[controller_index][1]
        print(f"Selected: {controllers[controller_index][0]}")

    def memory_overview(self):
        while True:
            self.clear_screen()
            self.print_banner()
            print("═══ MEMORY OVERVIEW ═══")
            print()
            
            for i, module in enumerate(self.current_modules, 1):
                print(f"DIMM {i}: {module.name}")
                print(f"  Type: {module.memory_type.value} | IC: {module.ic_type.value}")
                print(f"  Current: {module.current_speed} MHz @ {module.current_voltage:.3f}V")
                print(f"  Timings: {'-'.join(map(str, module.current_timings))} | Temp: {module.temperature:.1f}°C")
                print(f"  Stability: {module.stability_score}% | Errors: {module.errors}")
                print()
                
            print("Memory Controller Info:")
            print(f"  Quality: {self.memory_controller.imc_quality}/10")
            print(f"  Command Rate: {self.memory_controller.current_command_rate}T")
            if self.current_modules[0].memory_type == MemoryType.DDR5:
                print(f"  Gear Mode: {self.memory_controller.current_gear_mode}")
            print(f"  VCCIO: {self.memory_controller.vccio_voltage:.3f}V")
            print(f"  VCCSA: {self.memory_controller.vccsa_voltage:.3f}V")
            print()
            
            print("1. Back to Main Menu")
            choice = input("Select option: ").strip()
            
            if choice == "1":
                break

    def load_game_data(self):
        return {}
        
    def save_game(self):
        pass
        
    def load_game(self):
        print("Load game functionality not implemented yet.")
        input("Press Enter to continue...")
        
    def overclocking_lab(self):
        while True:
            self.clear_screen()
            self.print_banner()
            print("═══ OVERCLOCKING LABORATORY ═══")
            print()
            
            module = self.current_modules[0]  # Focus on first module
            print(f"Current Settings - {module.name}")
            print(f"Frequency: {module.current_speed} MHz")
            print(f"Primary Timings: {'-'.join(map(str, module.current_timings[:4]))}")
            print(f"Voltage: {module.current_voltage:.3f}V")
            print(f"Temperature: {module.temperature:.1f}°C")
            print(f"Stability: {module.stability_score}%")
            print()
            
            print("Overclocking Options:")
            print("1. Adjust Frequency")
            print("2. Adjust Primary Timings")
            print("3. Adjust Voltage")
            print("4. Secondary Timings (Advanced)")
            print("5. Apply XMP/DOCP Profile")
            print("6. Auto-Overclock Assistant")
            print("7. Reset to JEDEC")
            print("8. Quick Stability Test")
            print("9. Back to Main Menu")
            print()
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                self.adjust_frequency()
            elif choice == "2":
                self.adjust_primary_timings()
            elif choice == "3":
                self.adjust_voltage()
            elif choice == "4":
                self.adjust_secondary_timings()
            elif choice == "5":
                self.apply_xmp_profile()
            elif choice == "6":
                self.auto_overclock_assistant()
            elif choice == "7":
                self.reset_to_jedec()
            elif choice == "8":
                self.quick_stability_test()
            elif choice == "9":
                break
            else:
                print("Invalid option!")
                input("Press Enter to continue...")
                
    def adjust_frequency(self):
        self.clear_screen()
        print("═══ FREQUENCY ADJUSTMENT ═══")
        print()
        
        module = self.current_modules[0]
        print(f"Current Frequency: {module.current_speed} MHz")
        print(f"JEDEC Standard: {module.jedec_speed} MHz")
        print(f"XMP/DOCP Rating: {module.rated_speed} MHz")
        print()
        
        # Calculate safe ranges based on IC type
        safe_ranges = {
            MemoryIC.SAMSUNG_BDIE: (3200, 4400),
            MemoryIC.SAMSUNG_CDIE: (3000, 3800),
            MemoryIC.SAMSUNG_EDIE: (2800, 3400),
            MemoryIC.HYNIX_CJR: (3000, 3600),
            MemoryIC.HYNIX_DJR: (3200, 3800),
            MemoryIC.HYNIX_MFR: (2400, 3000),
            MemoryIC.MICRON_EDIE: (3000, 3600),
            MemoryIC.MICRON_BDIE: (4800, 6000) if module.memory_type == MemoryType.DDR5 else (3400, 4000),
        }
        
        min_freq, max_freq = safe_ranges.get(module.ic_type, (2133, 3200))
        print(f"Typical Range for {module.ic_type.value}: {min_freq}-{max_freq} MHz")
        print()
        
        try:
            new_freq = int(input(f"Enter new frequency ({module.jedec_speed}-{max_freq + 400}): "))
            
            if new_freq < module.jedec_speed:
                print("Warning: Running below JEDEC speed!")
            elif new_freq > max_freq + 200:
                print("Warning: Very aggressive overclock! High chance of instability.")
            
            # Update frequency and recalculate stability
            old_freq = module.current_speed
            module.current_speed = new_freq
            
            # Calculate stability impact
            freq_stress = abs(new_freq - module.rated_speed) / module.rated_speed
            stability_penalty = min(50, freq_stress * 100)
            
            module.stability_score = max(10, 100 - stability_penalty)
            module.temperature += (new_freq - old_freq) * 0.01  # Frequency affects temperature
            
            print(f"\nFrequency set to {new_freq} MHz")
            print(f"Estimated stability: {module.stability_score:.1f}%")
            print(f"Temperature: {module.temperature:.1f}°C")
            
        except ValueError:
            print("Invalid frequency!")
            
        input("\nPress Enter to continue...")
        
    def adjust_primary_timings(self):
        self.clear_screen()
        print("═══ PRIMARY TIMINGS ADJUSTMENT ═══")
        print()
        
        module = self.current_modules[0]
        timing_names = ["CL (CAS Latency)", "tRCD (RAS to CAS)", "tRP (RAS Precharge)", "tRAS (Row Active)"]
        
        print("Current Primary Timings:")
        for i, (name, value) in enumerate(zip(timing_names, module.current_timings)):
            print(f"{i+1}. {name}: {value}")
        print()
        
        # Show typical ranges for current IC
        typical_ranges = {
            MemoryIC.SAMSUNG_BDIE: {"CL": (14, 19), "tRCD": (14, 21), "tRP": (14, 21), "tRAS": (28, 42)},
            MemoryIC.SAMSUNG_CDIE: {"CL": (16, 22), "tRCD": (16, 24), "tRP": (16, 24), "tRAS": (32, 48)},
            MemoryIC.HYNIX_CJR: {"CL": (16, 20), "tRCD": (18, 22), "tRP": (18, 22), "tRAS": (36, 44)},
            MemoryIC.MICRON_BDIE: {"CL": (38, 46), "tRCD": (38, 48), "tRP": (38, 48), "tRAS": (76, 96)} if module.memory_type == MemoryType.DDR5 else {"CL": (15, 19), "tRCD": (17, 21), "tRP": (17, 21), "tRAS": (34, 42)}
        }
        
        ranges = typical_ranges.get(module.ic_type, {"CL": (15, 20), "tRCD": (15, 22), "tRP": (15, 22), "tRAS": (30, 44)})
        range_names = ["CL", "tRCD", "tRP", "tRAS"]
        
        print("Typical ranges for your IC:")
        for i, name in enumerate(range_names):
            min_val, max_val = ranges[name]
            print(f"{name}: {min_val}-{max_val}")
        print()
        
        try:
            choice = int(input("Select timing to adjust (1-4, 0 for all): "))
            
            if choice == 0:
                print("Enter all four primary timings:")
                new_timings = []
                for name in timing_names:
                    value = int(input(f"{name}: "))
                    new_timings.append(value)
                module.current_timings = new_timings
            elif 1 <= choice <= 4:
                new_value = int(input(f"Enter new value for {timing_names[choice-1]}: "))
                module.current_timings[choice-1] = new_value
            else:
                print("Invalid choice!")
                input("Press Enter to continue...")
                return
                
            # Calculate stability based on timing aggressiveness
            stability_bonus = 0
            for i, (name, value) in enumerate(zip(range_names, module.current_timings)):
                min_val, max_val = ranges[name]
                if value < min_val:
                    stability_bonus -= (min_val - value) * 5  # Penalty for too tight
                elif value > max_val:
                    stability_bonus += (value - max_val) * 2   # Bonus for loose timings
                    
            module.stability_score = max(10, min(100, module.stability_score + stability_bonus))
            
            print(f"\nTimings updated: {'-'.join(map(str, module.current_timings))}")
            print(f"Estimated stability: {module.stability_score:.1f}%")
            
        except ValueError:
            print("Invalid input!")
            
        input("\nPress Enter to continue...")
        
    def adjust_voltage(self):
        self.clear_screen()
        print("═══ VOLTAGE ADJUSTMENT ═══")
        print()
        
        module = self.current_modules[0]
        print(f"Current DRAM Voltage: {module.current_voltage:.3f}V")
        
        if module.memory_type == MemoryType.DDR4:
            print("DDR4 Safe Range: 1.200V - 1.500V")
            print("Daily Use Limit: 1.400V")
            print("Extreme OC Limit: 1.500V")
        else:
            print("DDR5 Safe Range: 1.100V - 1.400V") 
            print("Daily Use Limit: 1.300V")
            print("Extreme OC Limit: 1.400V")
        print()
        
        print("Memory Controller Voltages:")
        print(f"VCCIO: {self.memory_controller.vccio_voltage:.3f}V")
        print(f"VCCSA: {self.memory_controller.vccsa_voltage:.3f}V")
        print()
        
        print("1. Adjust DRAM Voltage")
        print("2. Adjust VCCIO")
        print("3. Adjust VCCSA")
        print("4. Back")
        
        choice = input("Select option: ").strip()
        
        try:
            if choice == "1":
                new_voltage = float(input("Enter new DRAM voltage: "))
                max_safe = 1.5 if module.memory_type == MemoryType.DDR4 else 1.4
                
                if new_voltage > max_safe:
                    print(f"WARNING: Voltage exceeds safe limit of {max_safe}V!")
                    confirm = input("Continue anyway? (y/N): ").lower()
                    if confirm != 'y':
                        return
                        
                module.current_voltage = new_voltage
                
                # Higher voltage improves stability but increases temperature
                voltage_benefit = (new_voltage - 1.2) * 20 if module.memory_type == MemoryType.DDR4 else (new_voltage - 1.1) * 25
                module.stability_score = min(100, module.stability_score + voltage_benefit)
                module.temperature += (new_voltage - 1.2) * 15 if module.memory_type == MemoryType.DDR4 else (new_voltage - 1.1) * 18
                
                print(f"DRAM voltage set to {new_voltage:.3f}V")
                
            elif choice == "2":
                new_vccio = float(input("Enter new VCCIO voltage: "))
                self.memory_controller.vccio_voltage = new_vccio
                print(f"VCCIO set to {new_vccio:.3f}V")
                
            elif choice == "3":
                new_vccsa = float(input("Enter new VCCSA voltage: "))
                self.memory_controller.vccsa_voltage = new_vccsa
                print(f"VCCSA set to {new_vccsa:.3f}V")
                
        except ValueError:
            print("Invalid voltage!")
            
        input("\nPress Enter to continue...")
        
    def apply_xmp_profile(self):
        module = self.current_modules[0]
        print(f"Applying XMP/DOCP profile for {module.name}...")
        
        module.current_speed = module.rated_speed
        module.current_timings = list(module.rated_timings)
        module.current_voltage = module.voltage
        module.stability_score = 85  # XMP profiles are usually stable
        
        print(f"Profile applied: {module.rated_speed} MHz @ {'-'.join(map(str, module.rated_timings))}")
        input("Press Enter to continue...")
        
    def reset_to_jedec(self):
        module = self.current_modules[0]
        print("Resetting to JEDEC standards...")
        
        module.current_speed = module.jedec_speed
        module.current_timings = list(module.jedec_timings)
        module.current_voltage = 1.2 if module.memory_type == MemoryType.DDR4 else 1.1
        module.stability_score = 100
        module.temperature = self.ambient_temperature + 10
        
        print("Reset complete. All settings at JEDEC defaults.")
        input("Press Enter to continue...")
        
    def quick_stability_test(self):
        print("Running quick stability test...")
        module = self.current_modules[0]
        
        # Simulate testing with progress bar
        for i in range(5):
            print(f"Testing... {(i+1)*20}%")
            time.sleep(0.5)
            
        # Determine if settings are stable
        if module.stability_score > 80:
            print("✓ STABLE - No errors detected!")
        elif module.stability_score > 60:
            print("⚠ UNSTABLE - Minor errors detected")
            module.errors += random.randint(1, 5)
        else:
            print("✗ FAILED - System would crash!")
            module.errors += random.randint(5, 20)
            
        input("Press Enter to continue...")
        
    def adjust_secondary_timings(self):
        print("Advanced secondary timing adjustment coming soon...")
        print("This will include tRRD, tWTR, tRFC, and other critical timings.")
        input("Press Enter to continue...")
        
    def auto_overclock_assistant(self):
        print("Auto-overclock assistant coming soon...")
        print("This will provide guided overclocking based on your hardware.")
        input("Press Enter to continue...")
        
    def stress_testing_menu(self):
        while True:
            self.clear_screen()
            self.print_banner()
            print("═══ STRESS TESTING SUITE ═══")
            print()
            
            module = self.current_modules[0]
            print(f"Current Configuration:")
            print(f"  {module.current_speed} MHz @ {'-'.join(map(str, module.current_timings[:4]))}")
            print(f"  Voltage: {module.current_voltage:.3f}V | Temp: {module.temperature:.1f}°C")
            print(f"  Stability Score: {module.stability_score}% | Errors: {module.errors}")
            print()
            
            print("Available Stress Tests:")
            print("1. MemTest86-style Test (Light)")
            print("2. Prime95 Blend Test (Medium)")
            print("3. AIDA64 Memory Test (Heavy)")
            print("4. Y-Cruncher Stress Test (Extreme)")
            print("5. Custom Test Duration")
            print("6. View Test History")
            print("7. Back to Main Menu")
            print()
            
            choice = input("Select test: ").strip()
            
            if choice == "1":
                self.run_stress_test("MemTest86", 10, "light")
            elif choice == "2":
                self.run_stress_test("Prime95 Blend", 20, "medium")
            elif choice == "3":
                self.run_stress_test("AIDA64 Memory", 30, "heavy")
            elif choice == "4":
                self.run_stress_test("Y-Cruncher", 60, "extreme")
            elif choice == "5":
                self.custom_stress_test()
            elif choice == "6":
                self.view_test_history()
            elif choice == "7":
                break
            else:
                print("Invalid option!")
                input("Press Enter to continue...")
                
    def run_stress_test(self, test_name: str, duration: int, intensity: str):
        self.clear_screen()
        print(f"═══ {test_name.upper()} STRESS TEST ═══")
        print()
        
        module = self.current_modules[0]
        print(f"Testing: {module.current_speed} MHz @ {module.current_voltage:.3f}V")
        print(f"Duration: {duration} seconds")
        print(f"Intensity: {intensity.upper()}")
        print()
        
        # Calculate failure probability based on stability score and intensity
        intensity_multipliers = {"light": 0.5, "medium": 1.0, "heavy": 1.5, "extreme": 2.0}
        failure_chance = (100 - module.stability_score) * intensity_multipliers[intensity] / 100
        
        # Temperature rises during testing
        temp_increase = {"light": 5, "medium": 10, "heavy": 15, "extreme": 20}[intensity]
        original_temp = module.temperature
        module.temperature += temp_increase
        
        print("Starting test...")
        print("Press Ctrl+C to abort (may cause instability!)")
        print()
        
        try:
            errors_found = 0
            for i in range(duration):
                progress = (i + 1) / duration * 100
                print(f"\rProgress: [{('#' * int(progress/5)).ljust(20)}] {progress:.1f}% | Temp: {module.temperature:.1f}°C", end="", flush=True)
                
                # Check for errors based on failure chance
                if random.random() < failure_chance / duration:
                    errors_found += 1
                    
                # Temperature can cause additional instability
                if module.temperature > 85:
                    if random.random() < 0.1:  # High temp error chance
                        errors_found += 1
                        
                time.sleep(0.1)  # Speed up for demo
                
            print("\n")
            
            # Test results
            if errors_found == 0:
                print("✓ TEST PASSED - No errors detected!")
                print("Your overclock is stable for this workload.")
                module.stability_score = min(100, module.stability_score + 2)
            elif errors_found < 5:
                print(f"⚠ TEST UNSTABLE - {errors_found} errors detected")
                print("Consider reducing frequency or loosening timings.")
                module.errors += errors_found
                module.stability_score = max(10, module.stability_score - 5)
            else:
                print(f"✗ TEST FAILED - {errors_found} errors detected!")
                print("This overclock is not stable. Reduce settings immediately.")
                module.errors += errors_found
                module.stability_score = max(10, module.stability_score - 15)
                
            # Cool down after test
            module.temperature = original_temp + 2  # Slight residual heat
            
        except KeyboardInterrupt:
            print("\n\nTest aborted by user!")
            print("Aborting stress tests can cause system instability.")
            module.stability_score = max(10, module.stability_score - 10)
            module.temperature = original_temp
            
        input("\nPress Enter to continue...")
        
    def custom_stress_test(self):
        self.clear_screen()
        print("═══ CUSTOM STRESS TEST ═══")
        print()
        
        try:
            duration = int(input("Test duration (seconds, 5-300): "))
            duration = max(5, min(300, duration))
            
            print("\nIntensity levels:")
            print("1. Light (Basic stability)")
            print("2. Medium (Standard validation)")  
            print("3. Heavy (Thorough testing)")
            print("4. Extreme (Maximum stress)")
            
            intensity_choice = input("Select intensity (1-4): ").strip()
            intensities = {"1": "light", "2": "medium", "3": "heavy", "4": "extreme"}
            intensity = intensities.get(intensity_choice, "medium")
            
            self.run_stress_test("Custom Test", duration, intensity)
            
        except ValueError:
            print("Invalid input!")
            input("Press Enter to continue...")
            
    def view_test_history(self):
        print("Test history feature coming soon...")
        print("This will track all your stress test results and show stability trends.")
        input("Press Enter to continue...")
        
    def temperature_monitor(self):
        while True:
            self.clear_screen()
            self.print_banner()
            print("═══ TEMPERATURE MONITORING ═══")
            print()
            
            module = self.current_modules[0]
            
            # Calculate heat generation from overclock
            base_temp = self.ambient_temperature + 10
            freq_heat = (module.current_speed - module.jedec_speed) * 0.005
            voltage_heat = (module.current_voltage - 1.2) * 20 if module.memory_type == MemoryType.DDR4 else (module.current_voltage - 1.1) * 25
            
            module.temperature = base_temp + freq_heat + voltage_heat
            
            print("Current Temperatures:")
            print(f"  Memory Modules: {module.temperature:.1f}°C")
            print(f"  Ambient: {self.ambient_temperature:.1f}°C")
            print()
            
            # Temperature status
            if module.temperature < 45:
                temp_status = "EXCELLENT"
                temp_color = "✓"
            elif module.temperature < 65:
                temp_status = "GOOD"
                temp_color = "○"
            elif module.temperature < 75:
                temp_status = "WARM"
                temp_color = "⚠"
            elif module.temperature < 85:
                temp_status = "HOT"
                temp_color = "⚠"
            else:
                temp_status = "CRITICAL"
                temp_color = "✗"
                
            print(f"Status: {temp_color} {temp_status}")
            print()
            
            # Temperature effects on stability
            if module.temperature > 75:
                temp_penalty = (module.temperature - 75) * 2
                print(f"High temperature reducing stability by {temp_penalty:.1f}%")
            print()
            
            print("Cooling Solutions:")
            print(f"Current: {self.cooling_solution}")
            print("1. Stock Cooler (Basic)")
            print("2. Tower Air Cooler (Good)")
            print("3. AIO Liquid Cooler (Better)")
            print("4. Custom Loop (Best)")
            print("5. Add Case Fans")
            print("6. Adjust Ambient Temperature")
            print("7. Live Temperature Graph")
            print("8. Back to Main Menu")
            print()
            
            choice = input("Select option: ").strip()
            
            if choice == "1":
                self.cooling_solution = "Stock Cooler"
                self.ambient_temperature = 28
                print("Stock cooling applied. Budget-friendly but limited cooling.")
            elif choice == "2":
                self.cooling_solution = "Tower Air Cooler"
                self.ambient_temperature = 25
                print("Tower cooler installed. Good performance for the price.")
            elif choice == "3":
                self.cooling_solution = "AIO Liquid Cooler"
                self.ambient_temperature = 22
                print("AIO cooler installed. Excellent cooling performance.")
            elif choice == "4":
                self.cooling_solution = "Custom Loop"
                self.ambient_temperature = 20
                print("Custom loop installed. Maximum cooling potential!")
            elif choice == "5":
                self.add_case_fans()
            elif choice == "6":
                self.adjust_ambient_temp()
            elif choice == "7":
                self.live_temp_graph()
            elif choice == "8":
                break
            else:
                print("Invalid option!")
                
            if choice in ["1", "2", "3", "4"]:
                input("Press Enter to continue...")
                
    def add_case_fans(self):
        print("Adding case fans...")
        print("Better airflow reduces ambient temperature by 2-3°C")
        self.ambient_temperature = max(18, self.ambient_temperature - 2.5)
        print(f"Ambient temperature now: {self.ambient_temperature:.1f}°C")
        input("Press Enter to continue...")
        
    def adjust_ambient_temp(self):
        print("Ambient Temperature Adjustment")
        print("(Simulates room temperature, AC, seasonal changes)")
        print()
        try:
            new_temp = float(input(f"Enter ambient temperature (15-35°C, current: {self.ambient_temperature:.1f}): "))
            new_temp = max(15, min(35, new_temp))
            self.ambient_temperature = new_temp
            print(f"Ambient temperature set to {new_temp:.1f}°C")
        except ValueError:
            print("Invalid temperature!")
        input("Press Enter to continue...")
        
    def live_temp_graph(self):
        self.clear_screen()
        print("═══ LIVE TEMPERATURE MONITORING ═══")
        print("Monitoring for 30 seconds... Press Ctrl+C to stop early")
        print()
        
        try:
            for i in range(30):
                module = self.current_modules[0]
                
                # Simulate small temperature fluctuations
                temp_variation = random.uniform(-1, 1)
                display_temp = module.temperature + temp_variation
                
                # Create simple ASCII graph
                bar_length = int(display_temp / 2)  # Scale for display
                bar = "█" * bar_length
                
                print(f"\rTemp: {display_temp:5.1f}°C [{bar:<40}] {i+1:2d}s", end="", flush=True)
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
            
        print("\n\nTemperature monitoring stopped.")
        input("Press Enter to continue...")
        
    def knowledge_base(self):
        while True:
            self.clear_screen()
            self.print_banner()
            print("═══ OVERCLOCKING KNOWLEDGE BASE ═══")
            print("Learn real RAM overclocking principles!")
            print()
            
            print("Topics:")
            print("1. Memory IC Types & Characteristics")
            print("2. Primary Timings Explained")
            print("3. Secondary & Tertiary Timings")
            print("4. Voltage Scaling & Safety")
            print("5. Temperature Management")
            print("6. Stability Testing Methods")
            print("7. Memory Controllers & Compatibility")
            print("8. Binning & Quality Assessment")
            print("9. Advanced Techniques")
            print("10. Troubleshooting Guide")
            print("11. Back to Main Menu")
            print()
            
            choice = input("Select topic: ").strip()
            
            if choice == "1":
                self.kb_memory_ics()
            elif choice == "2":
                self.kb_primary_timings()
            elif choice == "3":
                self.kb_secondary_timings()
            elif choice == "4":
                self.kb_voltage_scaling()
            elif choice == "5":
                self.kb_temperature_mgmt()
            elif choice == "6":
                self.kb_stability_testing()
            elif choice == "7":
                self.kb_memory_controllers()
            elif choice == "8":
                self.kb_binning()
            elif choice == "9":
                self.kb_advanced_techniques()
            elif choice == "10":
                self.kb_troubleshooting()
            elif choice == "11":
                break
            else:
                print("Invalid option!")
                input("Press Enter to continue...")
                
    def kb_memory_ics(self):
        self.clear_screen()
        print("═══ MEMORY IC TYPES & CHARACTERISTICS ═══")
        print()
        print("SAMSUNG B-DIE (The Golden Standard)")
        print("• Best overall scaling and tight timing capability")
        print("• Loves voltage (1.45V+ for best results)")
        print("• Can often do CL14 at 3200+ MHz")
        print("• Responds well to TRCDRD/TRCDWR tuning")
        print("• Found in premium kits, getting rare")
        print()
        print("SAMSUNG C-DIE")
        print("• Decent frequency scaling, voltage sensitive")
        print("• Can't take as much voltage as B-Die")
        print("• Usually requires looser timings than B-Die")
        print("• Good budget alternative")
        print()
        print("HYNIX CJR/DJR")
        print("• CJR: Budget option, limited OC potential")
        print("• DJR: Improved version, better scaling")
        print("• Both prefer lower voltages (1.35V range)")
        print("• Can achieve good results with patience")
        print()
        print("MICRON E-DIE & B-DIE")
        print("• E-Die: Rev.E, solid performer")
        print("• B-Die: Different from Samsung, DDR5 focus")
        print("• Temperature sensitive")
        print("• Good price/performance ratio")
        print()
        print("How to identify your IC:")
        print("• Use Thaiphoon Burner or similar tools")
        print("• Check kit specifications and reviews")
        print("• Look at die revision codes")
        print()
        input("Press Enter to continue...")
        
    def kb_primary_timings(self):
        self.clear_screen()
        print("═══ PRIMARY TIMINGS EXPLAINED ═══")
        print()
        print("CL (CAS Latency)")
        print("• Time between read command and data output")
        print("• Most important for performance")
        print("• Lower = better, but harder to achieve")
        print("• Buildzoid's rule: Start loose, tighten gradually")
        print()
        print("tRCD (RAS to CAS Delay)")
        print("• Time between row activation and column access")
        print("• Often = CL on good ICs")
        print("• Can sometimes be tighter than CL")
        print("• DDR5 splits into TRCDRD/TRCDWR")
        print()
        print("tRP (RAS Precharge)")
        print("• Time to close a row before opening another")
        print("• Usually matches tRCD")
        print("• Critical for stability")
        print("• Affects sequential access patterns")
        print()
        print("tRAS (Row Active Time)")
        print("• Minimum time a row must stay open")
        print("• Usually tRCD + tRP + 2-4")
        print("• Higher values sometimes improve stability")
        print("• Less performance impact than other primaries")
        print()
        print("Tuning Strategy:")
        print("1. Start with XMP/JEDEC timings")
        print("2. Tighten CL first")
        print("3. Match tRCD to CL if possible")
        print("4. Set tRP = tRCD")
        print("5. Calculate tRAS = tRCD + tRP + 2")
        print()
        input("Press Enter to continue...")
        
    def kb_secondary_timings(self):
        self.clear_screen()
        print("═══ SECONDARY & TERTIARY TIMINGS ═══")
        print()
        print("KEY SECONDARY TIMINGS:")
        print()
        print("tRRD_S/tRRD_L (Row to Row Delay)")
        print("• Time between activating rows in same/different bank groups")
        print("• S = Same bank group, L = Different bank group")
        print("• Lower = better, but can cause instability")
        print("• Often 4/6 or 6/8 for tight setups")
        print()
        print("tWTR_S/tWTR_L (Write to Read Delay)")
        print("• Time between write and read commands")
        print("• Critical for mixed workloads")
        print("• Samsung B-Die can often do 4/8")
        print("• Other ICs may need 4/12 or higher")
        print()
        print("tRFC (Refresh Cycle Time)")
        print("• Time for complete refresh operation")
        print("• Varies by density (8Gb, 16Gb, etc.)")
        print("• Can often be reduced from JEDEC values")
        print("• 8Gb: ~312ns, 16Gb: ~560ns typical")
        print()
        print("tFAW (Four Bank Activate Window)")
        print("• Maximum row activations in time window")
        print("• Usually 16-20 for most setups")
        print("• Can sometimes be tightened to 12-16")
        print()
        print("TERTIARY TIMINGS:")
        print("• tREFI, tRTP, tWR, tCWL, etc.")
        print("• Fine-tuning for last % of performance")
        print("• Require extensive testing")
        print("• Often unstable if too aggressive")
        print()
        input("Press Enter to continue...")
        
    def kb_voltage_scaling(self):
        self.clear_screen()
        print("═══ VOLTAGE SCALING & SAFETY ═══")
        print()
        print("DDR4 VOLTAGE GUIDELINES:")
        print("• JEDEC: 1.20V")
        print("• XMP: Usually 1.35V")
        print("• Daily safe: Up to 1.40V")
        print("• Extreme OC: 1.45-1.50V (cooling dependent)")
        print("• Danger zone: 1.55V+ (risk of degradation)")
        print()
        print("DDR5 VOLTAGE GUIDELINES:")
        print("• JEDEC: 1.10V")
        print("• XMP: Usually 1.25-1.35V")
        print("• Daily safe: Up to 1.35V")
        print("• Extreme OC: 1.40V (with good cooling)")
        print("• Danger zone: 1.45V+ (high degradation risk)")
        print()
        print("VOLTAGE SCALING BEHAVIOR:")
        print("• Samsung B-Die: Loves voltage, scales well to 1.5V+")
        print("• Samsung C-Die: Voltage sensitive, 1.4V+ can hurt")
        print("• Hynix: Generally prefers lower voltages")
        print("• Micron: Temperature sensitive at high voltage")
        print()
        print("MEMORY CONTROLLER VOLTAGES:")
        print("• VCCIO: IMC I/O voltage (0.95-1.2V typical)")
        print("• VCCSA: System Agent voltage (1.0-1.3V typical)")
        print("• Can help with high frequency stability")
        print("• Start with small increases (0.05V steps)")
        print()
        print("BUILDZOID'S VOLTAGE WISDOM:")
        print("• 'Voltage is the lazy man's timing adjustment'")
        print("• Always try tightening timings before adding voltage")
        print("• Temperature matters more than voltage for longevity")
        print("• Some ICs respond better to frequency than voltage")
        print()
        input("Press Enter to continue...")
        
    def kb_temperature_mgmt(self):
        self.clear_screen()
        print("═══ TEMPERATURE MANAGEMENT ═══")
        print()
        print("TEMPERATURE TARGETS:")
        print("• Excellent: <45°C")
        print("• Good: 45-65°C")
        print("• Acceptable: 65-75°C")
        print("• Concerning: 75-85°C")
        print("• Critical: >85°C (throttling/errors)")
        print()
        print("HEAT SOURCES:")
        print("• Frequency: Each 100MHz ~1-2°C")
        print("• Voltage: Each 0.1V ~5-8°C")
        print("• Current: High-performance workloads")
        print("• Ambient: Room temperature baseline")
        print()
        print("COOLING SOLUTIONS:")
        print("• Passive: Heatspreaders (5-10°C improvement)")
        print("• Active: Fans over RAM (10-15°C improvement)")
        print("• Case airflow: Intake/exhaust balance")
        print("• Extreme: Direct cooling, LN2 (competitive OC)")
        print()
        print("TEMPERATURE EFFECTS:")
        print("• Stability: Higher temps = more errors")
        print("• Performance: Thermal throttling at extremes")
        print("• Longevity: <65°C for 24/7 use recommended")
        print("• IC specific: Some ICs more temp sensitive")
        print()
        print("MONITORING TIPS:")
        print("• Use HWiNFO64 or similar for real temps")
        print("• Check during stress testing, not idle")
        print("• Summer vs winter ambient differences")
        print("• GPU heat can affect RAM temperatures")
        print()
        input("Press Enter to continue...")
        
    def kb_stability_testing(self):
        self.clear_screen()
        print("═══ STABILITY TESTING METHODS ═══")
        print()
        print("TESTING HIERARCHY (Buildzoid's approach):")
        print("1. POST test - Does it boot?")
        print("2. Quick test - MemTest86 1-2 passes")
        print("3. Medium test - AIDA64 memory test 30+ min")
        print("4. Heavy test - Prime95 Blend or Y-Cruncher")
        print("5. Extreme test - 24h+ MemTest86")
        print()
        print("MEMTEST86:")
        print("• Gold standard for memory testing")
        print("• Boot from USB, runs outside OS")
        print("• Comprehensive pattern testing")
        print("• 1-2 passes usually sufficient for basic stability")
        print()
        print("PRIME95 BLEND:")
        print("• Tests CPU + memory subsystem")
        print("• Good for finding interaction issues")
        print("• More stressful than pure memory tests")
        print("• 30 minutes minimum, 2+ hours preferred")
        print()
        print("Y-CRUNCHER:")
        print("• Mathematical calculations")
        print("• Very memory intensive") 
        print("• Good for finding subtle timing issues")
        print("• Component stress test mode recommended")
        print()
        print("AIDA64 MEMORY TEST:")
        print("• Built-in Windows testing")
        print("• Convenient but less thorough")
        print("• Good for quick validation")
        print("• Not as reliable as MemTest86")
        print()
        print("TESTING PHILOSOPHY:")
        print("• 'Stable enough' depends on use case")
        print("• Gaming: Light testing often sufficient")
        print("• Workstation: Heavy testing required")
        print("• Server: Extreme testing mandatory")
        print()
        input("Press Enter to continue...")
        
    def kb_memory_controllers(self):
        self.clear_screen()
        print("═══ MEMORY CONTROLLERS & COMPATIBILITY ═══")
        print()
        print("INTEL MEMORY CONTROLLERS:")
        print("• Z690/Z790: Excellent DDR4/DDR5 support")
        print("• Z590/Z490: Strong DDR4, very high frequency capable")
        print("• Earlier gen: More limited, varies by chip quality")
        print("• Gear modes: Gear 1 (1:1) vs Gear 2 (1:2)")
        print()
        print("AMD MEMORY CONTROLLERS:")
        print("• Zen 3: Much improved over Zen 2")
        print("• Zen 4: Native DDR5 support")
        print("• Infinity Fabric: UCLK = MCLK preferred")
        print("• More sensitive to trace quality")
        print()
        print("MEMORY CONTROLLER QUALITY:")
        print("• Silicon lottery applies to IMCs too")
        print("• Better IMCs = higher stable frequencies")
        print("• Voltage scaling can help weaker IMCs")
        print("• Motherboard trace quality matters")
        print()
        print("GEAR MODES (Intel):")
        print("• Gear 1: 1:1 ratio, lower latency")
        print("• Gear 2: 1:2 ratio, higher bandwidth potential")
        print("• Crossover point ~DDR4-3600, DDR5-5600")
        print("• Depends on workload and timings")
        print()
        print("COMMAND RATE:")
        print("• 1T: Higher performance, harder to achieve")
        print("• 2T: More relaxed, better stability")
        print("• Some motherboards auto-adjust")
        print("• Can be manually forced in BIOS")
        print()
        print("MOTHERBOARD FACTORS:")
        print("• Layer count: More layers = better signaling")
        print("• Trace layout: Shorter traces preferred")
        print("• QVL lists: Tested configurations")
        print("• DIMM slot count: 2 slots easier than 4")
        print()
        input("Press Enter to continue...")
        
    def kb_binning(self):
        self.clear_screen()
        print("═══ BINNING & QUALITY ASSESSMENT ═══")
        print()
        print("WHAT IS BINNING?")
        print("• Manufacturers test and sort chips by quality")
        print("• Better bins = higher performance potential")
        print("• Reflected in XMP profiles and pricing")
        print("• Not all chips of same IC are equal")
        print()
        print("IDENTIFYING GOOD BINS:")
        print("• Low XMP voltage for given speed")
        print("• Tight XMP timings")
        print("• Premium kit pricing")
        print("• Review/forum feedback")
        print()
        print("TESTING YOUR BIN:")
        print("1. Start with loose timings at high frequency")
        print("2. Or tight timings at moderate frequency")
        print("3. Test voltage scaling response")
        print("4. Compare to known good samples")
        print()
        print("BIN QUALITY INDICATORS:")
        print("• Samsung B-Die examples:")
        print("  - Golden: 3200 C14 at 1.35V")
        print("  - Average: 3200 C16 at 1.35V")
        print("  - Poor: 3000 C16 at 1.35V")
        print()
        print("• Hynix CJR examples:")
        print("  - Good: 3600 C18 at 1.35V")
        print("  - Average: 3200 C16 at 1.35V")
        print("  - Poor: 3000 C16 at 1.35V")
        print()
        print("BIN LOTTERY TIPS:")
        print("• Buy from retailers with good return policies")
        print("• Check manufacturing dates (newer often better)")
        print("• Consider buying multiple kits for best bin")
        print("• Join overclocking communities for sample data")
        print()
        input("Press Enter to continue...")
        
    def kb_advanced_techniques(self):
        self.clear_screen()
        print("═══ ADVANCED OVERCLOCKING TECHNIQUES ═══")
        print()
        print("RTL/IOL TUNING:")
        print("• Round Trip Latency / I/O Latency")
        print("• Fine-tunes memory controller timing")
        print("• Can improve performance by 2-5%")
        print("• Requires careful testing")
        print()
        print("POWERDOWN MODES:")
        print("• Fast vs Slow exit modes")
        print("• Affects idle power and response")
        print("• Can impact stability")
        print("• Usually auto-managed by BIOS")
        print()
        print("TRAINING ALGORITHMS:")
        print("• Memory controller learns optimal settings")
        print("• Can be overridden manually")
        print("• ASUS: MaxxMEM, MSI: Memory Try It!")
        print("• Understanding helps with troubleshooting")
        print()
        print("SKEW CONTROL:")
        print("• Adjusts signal timing per bit")
        print("• Helps with high-frequency stability")
        print("• Usually automatic")
        print("• Manual tuning for extreme overclocks")
        print()
        print("BUILDZOID'S ADVANCED TIPS:")
        print("• 'Subtimings matter more than you think'")
        print("• 'Every IC has its own personality'")
        print("• 'Stability testing is never finished'")
        print("• 'Document everything - memory is finicky'")
        print()
        print("EXTREME OVERCLOCKING:")
        print("• LN2 cooling for competitions")
        print("• Single-stick vs dual-stick tradeoffs")
        print("• Cold boot bugs and workarounds")
        print("• Validation software choices")
        print()
        input("Press Enter to continue...")
        
    def kb_troubleshooting(self):
        self.clear_screen()
        print("═══ TROUBLESHOOTING GUIDE ═══")
        print()
        print("COMMON ISSUES & SOLUTIONS:")
        print()
        print("WON'T POST / BOOT:")
        print("• Clear CMOS, start with JEDEC")
        print("• Check CPU memory controller support")
        print("• Verify kit compatibility with motherboard")
        print("• Try single stick to isolate bad DIMM")
        print()
        print("BOOTS BUT UNSTABLE:")
        print("• Increase DRAM voltage by 0.05V")
        print("• Loosen primary timings by 1-2")
        print("• Check/increase VCCIO and VCCSA")
        print("• Reduce frequency by 200MHz")
        print()
        print("PERFORMANCE REGRESSION:")
        print("• Check for gear mode changes")
        print("• Verify command rate (1T vs 2T)")
        print("• Look for thermal throttling")
        print("• Compare with known good settings")
        print()
        print("RANDOM ERRORS:")
        print("• Usually timing-related")
        print("• Increase tRAS, tRFC first")
        print("• Check secondary timings")
        print("• Test individual sticks")
        print()
        print("MEMORY TRAINING FAILURES:")
        print("• Power cycle system completely")
        print("• Update BIOS to latest version")
        print("• Try different DIMM slots")
        print("• Adjust PLL voltages")
        print()
        print("BUILDZOID'S DIAGNOSTIC APPROACH:")
        print("1. Establish baseline (JEDEC works?)")
        print("2. Isolate variables (change one thing)")
        print("3. Test systematically")
        print("4. Document everything")
        print("5. When in doubt, add voltage")
        print("6. If voltage doesn't help, loosen timings")
        print()
        input("Press Enter to continue...")
        
    def show_achievements(self):
        print("Achievements system will be implemented next.")
        input("Press Enter to continue...")
        
    def settings_menu(self):
        print("Settings menu will be implemented next.")
        input("Press Enter to continue...")

if __name__ == "__main__":
    game = RAMOverclockGame()
    try:
        game.main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting game...")
        sys.exit(0)
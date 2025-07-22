#!/usr/bin/env python3
"""
KiCad Circuit Generator for CR2032 Battery + Switch + LED Circuit
Creates schematic and PCB files directly without requiring full KiCad installation
"""

import os
import json
from datetime import datetime
from pathlib import Path

class KiCadCircuitGenerator:
    """Generate KiCad schematic and PCB files for simple circuits"""
    
    def __init__(self, project_name="cr2032_led_circuit"):
        self.project_name = project_name
        self.project_dir = Path(project_name)
        self.project_dir.mkdir(exist_ok=True)
        
    def create_schematic_file(self):
        """Create KiCad schematic (.sch) file for CR2032 + Switch + LED circuit"""
        schematic_content = '''EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "CR2032 LED Circuit"
Date "{date}"
Rev "1.0"
Comp ""
Comment1 "Simple LED circuit with CR2032 battery and switch"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr

$Comp
L Device:Battery_Cell BT1
U 1 1 60000001
P 2000 3000
F 0 "BT1" H 2118 3096 50  0000 L CNN
F 1 "CR2032" H 2118 3005 50  0000 L CNN
F 2 "Battery:BatteryHolder_Keystone_3000_1x12mm" H 2000 3060 50  0001 C CNN
F 3 "~" H 2000 3060 50  0001 C CNN
    1    2000 3000
    1    0    0    -1  
$EndComp

$Comp
L Switch:SW_Push SW1
U 1 1 60000002
P 3500 2800
F 0 "SW1" H 3500 3085 50  0000 C CNN
F 1 "SW_Push" H 3500 2994 50  0000 C CNN
F 2 "Button_Switch_THT:SW_PUSH_6mm" H 3500 3000 50  0001 C CNN
F 3 "~" H 3500 3000 50  0001 C CNN
    1    3500 2800
    1    0    0    -1  
$EndComp

$Comp
L Device:LED D1
U 1 1 60000003
P 5000 3000
F 0 "D1" V 5039 2882 50  0000 R CNN
F 1 "LED" V 4948 2882 50  0000 R CNN
F 2 "LED_THT:LED_D5.0mm" H 5000 3000 50  0001 C CNN
F 3 "~" H 5000 3000 50  0001 C CNN
    1    5000 3000
    0    -1   -1   0   
$EndComp

$Comp
L Device:R R1
U 1 1 60000004
P 5000 2500
F 0 "R1" H 5070 2546 50  0000 L CNN
F 1 "330R" H 5070 2455 50  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 4930 2500 50  0001 C CNN
F 3 "~" H 5000 2500 50  0001 C CNN
    1    5000 2500
    1    0    0    -1  
$EndComp

Wire Wire Line
    2000 2800 2000 2700
Wire Wire Line
    2000 2700 3300 2700
Wire Wire Line
    3300 2700 3300 2800
Wire Wire Line
    3700 2800 3700 2700
Wire Wire Line
    3700 2700 5000 2700
Wire Wire Line
    5000 2700 5000 2650
Wire Wire Line
    5000 2350 5000 2300
Wire Wire Line
    5000 2300 5800 2300
Wire Wire Line
    5800 2300 5800 3500
Wire Wire Line
    5800 3500 2000 3500
Wire Wire Line
    2000 3500 2000 3200
Wire Wire Line
    5000 2850 5000 2700
Connection ~ 5000 2700

$Comp
L power:+BATT #PWR01
U 1 1 60000005
P 2000 2700
F 0 "#PWR01" H 2000 2550 50  0001 C CNN
F 1 "+BATT" H 2015 2873 50  0000 C CNN
F 2 "" H 2000 2700 50  0001 C CNN
F 3 "" H 2000 2700 50  0001 C CNN
    1    2000 2700
    1    0    0    -1  
$EndComp

$Comp
L power:GND #PWR02
U 1 1 60000006
P 2000 3500
F 0 "#PWR02" H 2000 3250 50  0001 C CNN
F 1 "GND" H 2005 3327 50  0000 C CNN
F 2 "" H 2000 3500 50  0001 C CNN
F 3 "" H 2000 3500 50  0001 C CNN
    1    2000 3500
    1    0    0    -1  
$EndComp

Connection ~ 2000 2700
Connection ~ 2000 3500

$EndSCHEMATC
'''.format(date=datetime.now().strftime("%Y-%m-%d"))
        
        schematic_path = self.project_dir / f"{self.project_name}.sch"
        with open(schematic_path, 'w') as f:
            f.write(schematic_content)
        
        return schematic_path
    
    def create_pcb_file(self):
        """Create KiCad PCB (.kicad_pcb) file"""
        pcb_content = '''(kicad_pcb (version 20171130) (host pcbnew 5.1.10)

  (general
    (thickness 1.6)
    (drawings 0)
    (tracks 6)
    (zones 0)
    (modules 4)
    (nets 3)
  )

  (page A4)
  (layers
    (0 F.Cu signal)
    (31 B.Cu signal)
    (32 B.Adhes user)
    (33 F.Adhes user)
    (34 B.Paste user)
    (35 F.Paste user)
    (36 B.SilkS user)
    (37 F.SilkS user)
    (38 B.Mask user)
    (39 F.Mask user)
    (40 Dwgs.User user)
    (41 Cmts.User user)
    (42 Eco1.User user)
    (43 Eco2.User user)
    (44 Edge.Cuts user)
    (45 Margin user)
    (46 B.CrtYd user)
    (47 F.CrtYd user)
    (48 B.Fab user)
    (49 F.Fab user)
  )

  (setup
    (last_trace_width 0.25)
    (trace_clearance 0.2)
    (zone_clearance 0.508)
    (zone_45_only no)
    (trace_min 0.2)
    (via_size 0.8)
    (via_drill 0.4)
    (via_min_size 0.4)
    (via_min_drill 0.3)
    (uvia_size 0.3)
    (uvia_drill 0.1)
    (uvias_allowed no)
    (uvia_min_size 0.2)
    (uvia_min_drill 0.1)
    (edge_width 0.05)
    (segment_width 0.2)
    (pcb_text_width 0.3)
    (pcb_text_size 1.5 1.5)
    (mod_edge_width 0.12)
    (mod_text_size 1 1)
    (mod_text_width 0.15)
    (pad_size 1.524 1.524)
    (pad_drill 0.762)
    (pad_to_mask_clearance 0.051)
    (solder_mask_min_width 0.25)
    (aux_axis_origin 0 0)
    (visible_elements FFFFFF7F)
    (pcbplotparams
      (layerselection 0x010fc_ffffffff)
      (usegerberextensions false)
      (usegerberattributes true)
      (usegerberadvancedattributes true)
      (creategerberjobfile true)
      (excludeedgelayer true)
      (linewidth 0.100000)
      (plotframeref false)
      (viasonmask false)
      (mode 1)
      (useauxorigin false)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.000000)
      (psnegative false)
      (psa4output false)
      (plotreference true)
      (plotvalue true)
      (plotinvisibletext false)
      (padsonsilk false)
      (subtractmaskfromsilk false)
      (outputformat 1)
      (mirror false)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory ""))
  )

  (net 0 "")
  (net 1 "+BATT")
  (net 2 "GND")

  (net_class Default "This is the default net class."
    (clearance 0.2)
    (trace_width 0.25)
    (via_dia 0.8)
    (via_drill 0.4)
    (uvia_dia 0.3)
    (uvia_drill 0.1)
    (add_net "+BATT")
    (add_net "GND")
  )

  (module Battery:BatteryHolder_Keystone_3000_1x12mm (layer F.Cu) (tedit 589EE147) (tstamp 60000001)
    (at 140 100)
    (descr "CR2032 battery holder")
    (tags "CR2032 battery")
    (path /60000001)
    (fp_text reference BT1 (at 0 -8.89) (layer F.SilkS)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value CR2032 (at 0 8.89) (layer F.Fab)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (pad 1 thru_hole circle (at -9 0) (size 2 2) (drill 1) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
    (pad 2 thru_hole circle (at 9 0) (size 2 2) (drill 1) (layers *.Cu *.Mask)
      (net 2 "GND"))
  )

  (module Button_Switch_THT:SW_PUSH_6mm (layer F.Cu) (tedit 5A02FE31) (tstamp 60000002)
    (at 170 100)
    (descr "tactile push button, 6x6mm e.g. PHAP33xx series, height=4.3mm")
    (tags "tact sw push 6mm")
    (path /60000002)
    (fp_text reference SW1 (at 3.25 -2) (layer F.SilkS)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value SW_Push (at 3.25 6.7) (layer F.Fab)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (pad 1 thru_hole circle (at 0 0) (size 2 2) (drill 1) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
    (pad 2 thru_hole circle (at 6.5 0) (size 2 2) (drill 1) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
    (pad 3 thru_hole circle (at 0 4.5) (size 2 2) (drill 1) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
    (pad 4 thru_hole circle (at 6.5 4.5) (size 2 2) (drill 1) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
  )

  (module LED_THT:LED_D5.0mm (layer F.Cu) (tedit 587A3A7B) (tstamp 60000003)
    (at 200 100)
    (descr "LED, diameter 5.0mm, 2 pins")
    (tags "LED diameter 5.0mm 2 pins")
    (path /60000003)
    (fp_text reference D1 (at 1.27 -3.96) (layer F.SilkS)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value LED (at 1.27 3.96) (layer F.Fab)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (pad 1 thru_hole rect (at 0 0) (size 1.8 1.8) (drill 0.9) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
    (pad 2 thru_hole circle (at 2.54 0) (size 1.8 1.8) (drill 0.9) (layers *.Cu *.Mask)
      (net 2 "GND"))
  )

  (module Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal (layer F.Cu) (tedit 5AE5139B) (tstamp 60000004)
    (at 185 90)
    (descr "Resistor, Axial_DIN0207 series, Axial, Horizontal, pin pitch=7.62mm, 0.25W = 1/4W, length*diameter=6.3*2.5mm^2")
    (tags "Resistor Axial_DIN0207 series Axial Horizontal pin pitch 7.62mm 0.25W = 1/4W length 6.3mm diameter 2.5mm")
    (path /60000004)
    (fp_text reference R1 (at 3.81 -2.37) (layer F.SilkS)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (fp_text value 330R (at 3.81 2.37) (layer F.Fab)
      (effects (font (size 1 1) (thickness 0.15)))
    )
    (pad 1 thru_hole circle (at 0 0) (size 1.6 1.6) (drill 0.8) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
    (pad 2 thru_hole circle (at 7.62 0) (size 1.6 1.6) (drill 0.8) (layers *.Cu *.Mask)
      (net 1 "+BATT"))
  )

  (segment (start 149 100) (end 170 100) (width 0.25) (layer F.Cu) (net 1))
  (segment (start 176.5 100) (end 192.62 90) (width 0.25) (layer F.Cu) (net 1))
  (segment (start 192.62 90) (end 200 100) (width 0.25) (layer F.Cu) (net 1))
  (segment (start 149 100) (end 202.54 100) (width 0.25) (layer F.Cu) (net 2))

)
'''
        
        pcb_path = self.project_dir / f"{self.project_name}.kicad_pcb"
        with open(pcb_path, 'w') as f:
            f.write(pcb_content)
        
        return pcb_path
    
    def create_project_file(self):
        """Create KiCad project (.pro) file"""
        project_content = '''update=22/7/2025 12:00:00 AM
version=1
last_client=kicad
[general]
version=1
RootSch=
BoardNm=
[pcbnew]
version=1
LastNetListRead=
UseCmpFile=1
PadDrill=0.600000000000
PadDrillOvalY=0.600000000000
PadSizeH=1.500000000000
PadSizeV=1.500000000000
PcbTextSizeV=1.500000000000
PcbTextSizeH=1.500000000000
PcbTextThickness=0.300000000000
ModuleTextSizeV=1.000000000000
ModuleTextSizeH=1.000000000000
ModuleTextSizeThickness=0.150000000000
SolderMaskClearance=0.000000000000
SolderMaskMinWidth=0.000000000000
DrawSegmentWidth=0.200000000000
BoardOutlineThickness=0.100000000000
ModuleOutlineThickness=0.150000000000
[cvpcb]
version=1
NetIExt=net
[eeschema]
version=1
LibDir=
[eeschema/libraries]
'''
        
        project_path = self.project_dir / f"{self.project_name}.pro"
        with open(project_path, 'w') as f:
            f.write(project_content)
        
        return project_path
    
    def generate_circuit(self):
        """Generate complete KiCad project files"""
        print(f"Generating KiCad project: {self.project_name}")
        
        # Create all project files
        schematic_path = self.create_schematic_file()
        pcb_path = self.create_pcb_file()
        project_path = self.create_project_file()
        
        # Create readme with circuit description
        readme_content = f"""# {self.project_name.replace('_', ' ').title()}

## Circuit Description
Simple LED circuit powered by CR2032 battery with push button switch.

## Components:
- BT1: CR2032 3V Lithium Battery
- SW1: Momentary Push Button Switch  
- D1: LED (any color)
- R1: 330Ω Current Limiting Resistor

## Circuit Operation:
When the push button (SW1) is pressed, current flows from the positive terminal of the CR2032 battery (BT1) through the 330Ω resistor (R1), through the LED (D1), and back to the negative terminal of the battery, completing the circuit and lighting the LED.

## Files Generated:
- {schematic_path.name}: KiCad schematic file
- {pcb_path.name}: KiCad PCB layout file  
- {project_path.name}: KiCad project file

## Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        readme_path = self.project_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"✓ Schematic created: {schematic_path}")
        print(f"✓ PCB layout created: {pcb_path}")
        print(f"✓ Project file created: {project_path}")
        print(f"✓ Documentation created: {readme_path}")
        
        return {
            'project_dir': self.project_dir,
            'schematic': schematic_path,
            'pcb': pcb_path,
            'project': project_path,
            'readme': readme_path
        }

if __name__ == "__main__":
    generator = KiCadCircuitGenerator()
    result = generator.generate_circuit()
    print(f"\nKiCad project generated successfully in: {result['project_dir']}")
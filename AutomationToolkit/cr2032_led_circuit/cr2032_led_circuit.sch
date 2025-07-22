EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "CR2032 LED Circuit"
Date "2025-07-22"
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

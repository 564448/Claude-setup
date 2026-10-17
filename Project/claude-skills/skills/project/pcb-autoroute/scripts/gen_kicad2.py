"""CanSat carrier board Rev B generator (KiCad 8): real library footprints embedded, 40 x 45 mm, Teensy 4.0."""
import os, re, uuid, json, csv, math, shutil
OUT = os.environ.get("CANSAT_OUT", r"C:\Knight\Project\SPACE\Cansat\hardware")
LIB = os.path.join(OUT, "lib"); PRETTY = os.path.join(LIB, "cansat.pretty")
KFP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kfp")
os.makedirs(PRETTY, exist_ok=True)
for f in os.listdir(PRETTY): os.remove(os.path.join(PRETTY, f))
U = lambda: str(uuid.uuid4())
ROOT_UUID = U()
BW, BH = 40.0, 45.0

# ------------------------------------------------------------ s-expression parser
def parse_sexpr(s):
    tok = re.findall(r'"(?:[^"\\]|\\.)*"|[()]|[^\s()"]+', s)
    stack = [[]]
    for t in tok:
        if t == '(': stack.append([])
        elif t == ')': x = stack.pop(); stack[-1].append(x)
        else: stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]
def find(node, key):
    return [n for n in node if isinstance(n, list) and n and n[0] == key]
def first(node, key, default=None):
    f = find(node, key); return f[0] if f else default
def num(x): return float(x)

def load_kicad_mod(fname, newname=None):
    """Return FP dict: pads [(num,kind,shape,x,y,w,h,drill,rot,rratio)], gfx [(type,layer,params)], crtyd bbox, body bbox."""
    tree = parse_sexpr(open(os.path.join(KFP, fname), encoding="utf-8").read())
    name = newname or tree[1]
    pads = []; gfx = []
    for n in tree[2:]:
        if not isinstance(n, list): continue
        if n[0] == "pad":
            pnum, kind, shape = n[1], n[2], n[3]
            at = first(n, "at"); x, y = num(at[1]), num(at[2]); rot = num(at[3]) if len(at) > 3 else 0.0
            sz = first(n, "size"); w, h = num(sz[1]), num(sz[2])
            dr = first(n, "drill"); drill = num(dr[1]) if dr and len(dr) > 1 and not isinstance(dr[1], list) else 0.0
            rr = first(n, "roundrect_rratio"); rratio = num(rr[1]) if rr else 0.25
            if shape == "custom":  # LGA-14 corner pads: use the plain pad size of their neighbours
                shape = "roundrect"; w, h = (0.625, 0.4) if abs(x) > 1.0 else (0.4, 0.625)
            if shape == "oval" and w == h: shape = "circle"
            lay = first(n, "layers"); layers = tuple(lay[1:]) if lay else None
            if shape == "roundrect" and abs(x) > 1.0 and w == 0.625: w = 0.625; h = 0.37   # LGA-14: 0.5 mm pitch -> 0.13 mm gap
            if shape == "roundrect" and abs(x) <= 1.0 and h == 0.625: w = 0.37; h = 0.625
            pads.append((str(pnum), kind, shape, x, y, w, h, drill, rot, rratio, layers))
        elif n[0] in ("fp_line", "fp_circle", "fp_rect"):
            layer = first(n, "layer")[1]
            if n[0] == "fp_circle":
                c = first(n, "center"); e = first(n, "end"); gfx.append(("circle", layer, (num(c[1]), num(c[2]), num(e[1]), num(e[2]))))
            else:
                a = first(n, "start"); b = first(n, "end"); gfx.append((n[0][3:], layer, (num(a[1]), num(a[2]), num(b[1]), num(b[2]))))
    def bbox(layer):
        xs = []; ys = []
        for t, l, p in gfx:
            if l != layer: continue
            if t == "circle":
                r = math.hypot(p[2]-p[0], p[3]-p[1]); xs += [p[0]-r, p[0]+r]; ys += [p[1]-r, p[1]+r]
            else: xs += [p[0], p[2]]; ys += [p[1], p[3]]
        return (min(xs), min(ys), max(xs), max(ys)) if xs else None
    cy = bbox("F.CrtYd")
    if cy is None:
        xs = [p[3]-p[5]/2 for p in pads]+[p[3]+p[5]/2 for p in pads]; ys = [p[4]-p[6]/2 for p in pads]+[p[4]+p[6]/2 for p in pads]
        cy = (min(xs)-0.25, min(ys)-0.25, max(xs)+0.25, max(ys)+0.25)
    return dict(name=name, pads=pads, gfx=gfx, crtyd=cy, fab=bbox("F.Fab") or cy, src=fname)

# ------------------------------------------------------------ generated footprints (datasheet geometry)
def smd(num, x, y, w, h, shape="roundrect", rot=0.0): return (str(num), "smd", shape, x, y, w, h, 0.0, rot, 0.25, None)
def th(num, x, y, d=1.7, drill=1.0, shape="circle"): return (str(num), "thru_hole", shape, x, y, d, d, drill, 0.0, 0.25, None)
def gen_fp(name, pads, body, crtyd=None, silk=True, extra_crtyd=None):
    w, h = body
    gfx = [("rect", "F.Fab", (-w/2, -h/2, w/2, h/2))]
    if silk: gfx.append(("rect", "F.SilkS", (-w/2, -h/2, w/2, h/2)))
    cy = crtyd or (-w/2-0.25, -h/2-0.25, w/2+0.25, h/2+0.25)
    for r in (extra_crtyd or [cy]): gfx.append(("rect", "F.CrtYd", r))
    return dict(name=name, pads=pads, gfx=gfx, crtyd=cy, fab=(-w/2, -h/2, w/2, h/2), src=None, crtyd_list=extra_crtyd)

FP = {}
# Teensy 4.0 — 2 x 14 pins on 2.54 mm, rows 15.24 apart, 5-pin end row (29-33) opposite the USB end
t = [th(i+1, -7.62, -16.51+i*2.54, 1.6, 0.95) for i in range(14)] + [th(i+15, 7.62, -16.51+i*2.54, 1.6, 0.95) for i in range(14)] + [th(i+29, -5.08+i*2.54, 16.51, 1.6, 0.95) for i in range(5)]
FP["TEENSY40"] = gen_fp("TEENSY40", t, (17.78, 35.56))
# XBee 20-pin, 2.0 mm pitch, rows 22 mm apart (Digi 90002173 mechanical drawing). Courtyard = the two socket strips only.
x = [th(i+1, -11.0, -9.0+i*2.0, 1.5, 0.9) for i in range(10)] + [th(i+11, 11.0, 9.0-i*2.0, 1.5, 0.9) for i in range(10)]
FP["XBEE_TH"] = gen_fp("XBEE_TH", x, (24.4, 33.0), silk=False, crtyd=(-12.5, -16.5, 12.5, 16.5), extra_crtyd=[(-12.0, -10.0, -10.0, 10.0), (10.0, -10.0, 12.0, 10.0)])
# Quectel LC29H — Hardware Design V1.3 Fig. 19: 2 columns x 12 oval pads 2.5 x 0.8, x = ±6.3, pitch 1.1, 3 mm gap. Pin 1 top-left, 1-12 down the left, 13-24 up the right.
ys = [-7.0+i*1.1 for i in range(7)] + [2.6+i*1.1 for i in range(5)]
lc = [smd(i+1, -6.3, ys[i], 2.5, 0.8, "oval") for i in range(12)] + [smd(13+i, 6.3, ys[11-i], 2.5, 0.8, "oval") for i in range(12)]
FP["LC29H"] = gen_fp("LC29H", lc, (12.2, 16.0), silk=False, crtyd=(-7.65, -8.25, 7.65, 8.25))
# Bosch BMP585 — BST-BMP585-DS003-02 Fig. 22/29: 3.25 x 3.25, pads at ±1.225 / ±1.1, +25 µm per side. Pin 1 top-left (top view), CCW.
b = [smd(1, -1.225, -1.1, 0.55, 0.8), smd(2, -1.225, 0, 0.55, 1.06), smd(3, -1.225, 1.1, 0.55, 0.8), smd(4, 0, 1.1, 1.07, 0.8),
     smd(5, 1.225, 1.1, 0.55, 0.8), smd(6, 1.225, 0, 0.55, 1.06), smd(7, 1.225, -1.1, 0.55, 0.8), smd(8, 0, -1.1, 1.07, 0.8)]
FP["BMP585"] = gen_fp("BMP585", b, (3.25, 3.25), silk=False)
# 5 x 5 mm SMD magnetic buzzer (generic 2-pad; verify against the part you buy)
FP["BUZZER_SMD_5x5"] = gen_fp("BUZZER_SMD_5x5", [smd(1, -2.1, 0, 1.2, 1.6), smd(2, 2.1, 0, 1.2, 1.6)], (5.4, 5.4), silk=False)

LIBFP = {  # project name : KiCad library file
 "ESP32-WROOM-32E": "ESP32-WROOM-32.kicad_mod",   # -32E is land-pattern compatible with -32 (Espressif datasheet)
 "LGA-14_3x2.5mm_P0.5mm": "LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.kicad_mod",
 "LGA-12_2x2mm_P0.5mm": "LGA-12_2x2mm_P0.5mm.kicad_mod",
 "VSSOP-10_3x3mm_P0.5mm": "VSSOP-10_3x3mm_P0.5mm.kicad_mod",
 "QFN-16-1EP_3x3mm_P0.5mm": "QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm.kicad_mod",
 "L_Coilcraft_XFL4020": "L_Coilcraft_XxL4020.kicad_mod",
 "SOIC-8_5.23x5.23mm_P1.27mm": "SOIC-8_5.23x5.23mm_P1.27mm.kicad_mod",
 "U.FL_Hirose_U.FL-R-SMT-1_Vertical": "U.FL_Hirose_U.FL-R-SMT-1_Vertical.kicad_mod",
 "JST_PH_B2B-PH-SM4-TB_Vertical": "JST_PH_B2B-PH-SM4-TB_1x02-1MP_P2.00mm_Vertical.kicad_mod",
 "JST_SH_BM02B-SRSS-TB_Vertical": "JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical.kicad_mod",
 "JST_SH_BM04B-SRSS-TB_Vertical": "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical.kicad_mod",
 "JST_SH_BM06B-SRSS-TB_Vertical": "JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical.kicad_mod",
 "R_0402": "R_0402_1005Metric.kicad_mod", "R_0805": "R_0805_2012Metric.kicad_mod", "R_1206": "R_1206_3216Metric.kicad_mod", "R_2512": "R_2512_6332Metric.kicad_mod",
 "C_0402": "C_0402_1005Metric.kicad_mod", "C_0805": "C_0805_2012Metric.kicad_mod", "C_1210": "C_1210_3225Metric.kicad_mod",
 "D_SOD-123": "D_SOD-123.kicad_mod", "SOT-23": "SOT-23.kicad_mod",
}
for k, v in LIBFP.items(): FP[k] = load_kicad_mod(v, k)
FP["ESP32-WROOM-32E"]["crtyd_list"] = [(-9.75, -9.72, 9.75, 10.5), (-14.25, -21.0, 14.25, -9.72)]
FP["ESP32-WROOM-32E"]["gfx"] = [g for g in FP["ESP32-WROOM-32E"]["gfx"] if not g[1].endswith("SilkS")]

# ------------------------------------------------------------ components
G = "GND"; V3 = "+3V3"; V5 = "+5V"
COMP = []
def add(ref, value, sym, fp, pinspec, pcb, desc=""):
    COMP.append(dict(ref=ref, value=value, sym=sym, fp=fp, pins=[(str(a), b, c, d) for a, b, c, d in pinspec], pcb=pcb, desc=desc))
def c(ref, val, fp, n1, n2, pcb, desc=""): add(ref, val, "C", fp, [(1, "1", n1, "L"), (2, "2", n2, "R")], pcb, desc)
def r(ref, val, fp, n1, n2, pcb, desc=""): add(ref, val, "R", fp, [(1, "1", n1, "L"), (2, "2", n2, "R")], pcb, desc)

add("U1", "Teensy 4.0", "TEENSY40", "TEENSY40", [
 (1,"GND",G,"L"),(2,"D0/RX1","XB_DOUT","L"),(3,"D1/TX1","XB_DIN","L"),(4,"D2",None,"L"),(5,"D3",None,"L"),
 (6,"D4","XB_RST","L"),(7,"D5","XB_RSSI","L"),(8,"D6","XB_SLP","L"),(9,"D7/RX2","GPS_TX","L"),(10,"D8/TX2","GPS_RX","L"),
 (11,"D9","FLASH_CS","L"),(12,"D10","CAM_CS","L"),(13,"D11/MOSI","SPI_MOSI","L"),(14,"D12/MISO","SPI_MISO","L"),
 (15,"VIN",V5,"R"),(16,"AGND",G,"R"),(17,"3V3_OUT",None,"R"),(18,"D23","IMU_INT1","R"),(19,"D22/PWM","BUZ","R"),
 (20,"D21","GPS_RST","R"),(21,"D20","GPS_PPS","R"),(22,"D19/SCL","I2C_SCL","R"),(23,"D18/SDA","I2C_SDA","R"),
 (24,"D17","ESP_IO0","R"),(25,"D16","ESP_EN","R"),(26,"D15/RX3","ESP_TX","R"),(27,"D14/TX3","ESP_RX","R"),(28,"D13/SCK","SPI_SCK","R"),
 (29,"VBAT",None,"R"),(30,"3V3_END",None,"R"),(31,"GND_END",G,"R"),(32,"PROGRAM",None,"R"),(33,"ON_OFF",None,"R")],
 (20.0,35.5,90,"B"), "PJRC Teensy 4.0 (i.MX RT1062), bottom side, USB toward x=40")
add("U2", "XBee-PRO 900HP", "XBEE_S3B", "XBEE_TH", [
 (1,"VCC",V3,"L"),(2,"DOUT","XB_DOUT","L"),(3,"DIN","XB_DIN","L"),(4,"DIO12",None,"L"),(5,"~RESET","XB_RST","L"),
 (6,"RSSI/PWM0","XB_RSSI","L"),(7,"PWM1",None,"L"),(8,"RES",None,"L"),(9,"~DTR/SLEEP_RQ","XB_SLP","L"),(10,"GND",G,"L"),
 (11,"DIO4",None,"R"),(12,"~CTS",None,"R"),(13,"ON/~SLEEP",None,"R"),(14,"VREF",G,"R"),(15,"ASSOC",None,"R"),
 (16,"~RTS",None,"R"),(17,"AD3",None,"R"),(18,"AD2",None,"R"),(19,"AD1",None,"R"),(20,"AD0",None,"R")],
 (17.5,12.9,90,"F"), "Digi XBee-PRO 900HP S3B on 2 mm sockets (>= 4 mm standoff)")
esp = [(1,"GND",G,"L"),(2,"3V3",V3,"L"),(3,"EN","ESP_EN","L"),(4,"SENSOR_VP",None,"L"),(5,"SENSOR_VN",None,"L"),
 (6,"IO34",None,"L"),(7,"IO35",None,"L"),(8,"IO32",None,"L"),(9,"IO33",None,"L"),(10,"IO25",None,"L"),(11,"IO26",None,"L"),
 (12,"IO27",None,"L"),(13,"IO14",None,"L"),(14,"IO12",None,"L"),(15,"GND",G,"L"),(16,"IO13",None,"L"),(17,"SD2",None,"L"),
 (18,"SD3",None,"L"),(19,"CMD",None,"L"),(20,"CLK",None,"R"),(21,"SD0",None,"R"),(22,"SD1",None,"R"),(23,"IO15",None,"R"),
 (24,"IO2",None,"R"),(25,"IO0","ESP_IO0","R"),(26,"IO4",None,"R"),(27,"IO16",None,"R"),(28,"IO17",None,"R"),(29,"IO5",None,"R"),
 (30,"IO18",None,"R"),(31,"IO19",None,"R"),(32,"NC",None,"R"),(33,"IO21",None,"R"),(34,"RXD0","ESP_RX","R"),(35,"TXD0","ESP_TX","R"),
 (36,"IO22",None,"R"),(37,"IO23",None,"R"),(38,"GND",G,"R"),(39,"EP",G,"R")]
add("U3", "ESP32-WROOM-32E", "ESP32-WROOM-32E", "ESP32-WROOM-32E", esp, (9.3,13.0,270,"B"), "ESP-NOW modem; antenna overhangs the top edge (y<0); flashed through the Teensy (Serial3 bridge + EN/IO0)")
add("U4", "LC29H(AA)", "LC29H", "LC29H", [
 (1,"WAKEUP",None,"L"),(2,"FWD",None,"L"),(3,"1PPS","GPS_PPS","L"),(4,"WHEELTICK",None,"L"),(5,"D_SEL1",None,"L"),
 (6,"D_SEL2",None,"L"),(7,"VDD_EXT",None,"L"),(8,"RESET_N","GPS_RST","L"),(9,"VDD_RF",None,"L"),(10,"GND",G,"L"),
 (11,"RF_IN","GPS_RF","L"),(12,"GND",G,"L"),(13,"GND",G,"R"),(14,"ANT_ON",None,"R"),(15,"TXD2",None,"R"),(16,"RXD2",None,"R"),
 (17,"WI",None,"R"),(18,"I2C_SDA",None,"R"),(19,"I2C_SCL",None,"R"),(20,"TXD1","GPS_TX","R"),(21,"RXD1","GPS_RX","R"),
 (22,"V_BCKP",V3,"R"),(23,"VCC",V3,"R"),(24,"GND",G,"R")], (28.0,12.5,180,"B"), "Quectel LC29H GNSS, RF_IN at top-right next to J5")
add("J5", "U.FL GNSS", "UFL", "U.FL_Hirose_U.FL-R-SMT-1_Vertical", [(1,"SIG","GPS_RF","L"),(2,"GND",G,"R")], (37.8,6.6,0,"B"), "Hirose U.FL-R-SMT-1")
add("U5", "BMP585", "BMP585", "BMP585", [
 (1,"SCX","I2C_SCL","L"),(2,"SDX","I2C_SDA","L"),(3,"SDO",G,"L"),(4,"VDDIO",V3,"L"),
 (5,"INT",None,"R"),(6,"VSS",G,"R"),(7,"CSB",V3,"R"),(8,"VDD",V3,"R")], (4.5,5.2,0,"F"), "Barometer, I2C 0x46")
add("U6", "LSM6DSV32X", "LSM6DSV32X", "LGA-14_3x2.5mm_P0.5mm", [
 (1,"SDO/SA0",G,"L"),(2,"SDx",None,"L"),(3,"SCx",None,"L"),(4,"INT1","IMU_INT1","L"),(5,"VDDIO",V3,"L"),(6,"GND",G,"L"),(7,"GND",G,"L"),
 (8,"VDD",V3,"R"),(9,"INT2",None,"R"),(10,"AH1/Qvar1",None,"R"),(11,"AH2/Qvar2",None,"R"),(12,"CS",V3,"R"),(13,"SCL","I2C_SCL","R"),(14,"SDA","I2C_SDA","R")],
 (9.5,5.2,0,"F"), "IMU, I2C 0x6A")
add("U7", "LIS3MDL", "LIS3MDL", "LGA-12_2x2mm_P0.5mm", [
 (1,"SCL","I2C_SCL","L"),(2,"RES",G,"L"),(3,"GND",G,"L"),(4,"C1","MAG_C1","L"),(5,"VDD",V3,"L"),(6,"VDD_IO",V3,"L"),
 (7,"INT",None,"R"),(8,"DRDY",None,"R"),(9,"SDO/SA1",G,"R"),(10,"CS",V3,"R"),(11,"SDA","I2C_SDA","R"),(12,"RES",G,"R")],
 (14.5,5.2,0,"F"), "Magnetometer, I2C 0x1C")
ina = lambda a0, vbus, inn, inp: [(1,"A1",G,"L"),(2,"A0",a0,"L"),(3,"ALERT",None,"L"),(4,"SDA","I2C_SDA","L"),(5,"SCL","I2C_SCL","L"),
 (6,"VS",V3,"R"),(7,"GND",G,"R"),(8,"VBUS",vbus,"R"),(9,"IN-",inn,"R"),(10,"IN+",inp,"R")]
add("U8", "INA228", "INA228", "VSSOP-10_3x3mm_P0.5mm", ina(G,"VSYS","INA1_INN","INA1_INP"), (4.5,12.0,0,"F"), "Battery monitor, I2C 0x40")
add("U9", "INA226", "INA226", "VSSOP-10_3x3mm_P0.5mm", ina(V3,"SOL","INA2_INN","INA2_INP"), (13.0,12.0,0,"F"), "Solar monitor, I2C 0x41")
tps = lambda sw, ss, vo: [(1,"SW",sw,"R"),(2,"SW",sw,"R"),(3,"SW",sw,"R"),(4,"PG",None,"R"),(5,"FB",G,"L"),(6,"AGND",G,"L"),(7,"FSW",G,"L"),
 (8,"DEF",G,"L"),(9,"SS/TR",ss,"L"),(10,"AVIN","VSYS","L"),(11,"PVIN","VSYS","L"),(12,"PVIN","VSYS","L"),(13,"EN","BUCK_EN","L"),
 (14,"VOS",vo,"R"),(15,"PGND",G,"R"),(16,"PGND",G,"R"),(17,"EP",G,"R")]
add("U10", "TPS62133 (5V)", "TPS6213x", "QFN-16-1EP_3x3mm_P0.5mm", tps("SW5","SS5",V5), (24.8,5.8,0,"F"), "5 V buck, 3 A; FB/FSW/DEF to GND")
add("U11", "TPS62132 (3.3V)", "TPS6213x", "QFN-16-1EP_3x3mm_P0.5mm", tps("SW3","SS3",V3), (34.3,5.8,0,"F"), "3.3 V buck, 3 A")
add("U12", "W25N01GVSFIG", "W25N01G", "SOIC-8_5.23x5.23mm_P1.27mm", [
 (1,"~CS","FLASH_CS","L"),(2,"DO/IO1","SPI_MISO","L"),(3,"~WP/IO2",V3,"L"),(4,"GND",G,"L"),
 (5,"DI/IO0","SPI_MOSI","R"),(6,"CLK","SPI_SCK","R"),(7,"~HOLD/IO3",V3,"R"),(8,"VCC",V3,"R")], (30.2,15.0,0,"F"), "128 MB SPI NAND flight recorder (Teensy LittleFS), CS = D9")
add("L1", "2.2uH XFL4020", "L", "L_Coilcraft_XFL4020", [(1,"1","SW5","L"),(2,"2",V5,"R")], (29.5,5.8,0,"F"))
add("L2", "2.2uH XFL4020", "L", "L_Coilcraft_XFL4020", [(1,"1","SW3","L"),(2,"2",V3,"R")], (24.8,10.5,0,"F"))
c("C1","10uF 25V","C_0805","VSYS",G,(29.3,10.5,0,"F"),"U10 input")
c("C2","10uF 25V","C_0805","VSYS",G,(36.3,10.5,0,"F"),"U11 input")
c("C3","22uF 6.3V","C_0805",V5,G,(32.8,10.5,0,"F"),"U10 output")
c("C4","22uF 6.3V","C_0805",V3,G,(23.6,14.5,90,"F"),"U11 output")
c("C5","3.3nF","C_0402","SS5",G,(38.4,5.8,90,"F"))
c("C6","3.3nF","C_0402","SS3",G,(39.2,10.5,90,"F"))
c("C7","100nF","C_0402",V3,G,(4.5,8.2,0,"F"))
c("C8","100nF","C_0402",V3,G,(9.5,8.2,0,"F"))
c("C9","100nF","C_0402",V3,G,(14.5,8.2,0,"F"))
c("C10","100nF","C_0402","MAG_C1",G,(17.5,8.2,0,"F"),"LIS3MDL C1")
c("C11","100nF","C_0402",V3,G,(4.5,14.6,0,"F"))
c("C12","100nF","C_0402",V3,G,(13.0,14.8,0,"F"))
c("C13","100nF","C_0402","INA1_INP","INA1_INN",(8.0,12.0,90,"F"))
c("C14","100nF","C_0402","INA2_INP","INA2_INN",(16.5,12.2,90,"F"))
c("C15","22uF 6.3V","C_0805",V3,G,(2.8,17.0,90,"F"),"XBee bulk")
c("C16","22uF 6.3V","C_0805",V3,G,(2.8,21.0,90,"F"),"XBee bulk")
c("C17","22uF 6.3V","C_0805",V3,G,(5.6,20.5,0,"F"),"ESP32 bulk")
c("C18","100nF","C_0402",V3,G,(8.3,20.5,0,"F"),"ESP32")
c("C19","10uF 6.3V","C_0805",V3,G,(20.8,17.2,90,"F"),"LC29H VCC")
c("C20","100nF","C_0402",V3,G,(18.9,17.2,90,"F"),"LC29H VCC")
c("C22","1uF","C_0402","ESP_EN",G,(39.2,20.5,90,"F"),"ESP EN RC")
c("C23","100nF","C_0402",V3,G,(25.6,15.0,90,"F"),"W25N01G")
r("R1","10R","R_0402","VBAT","INA1_INP",(8.0,10.0,0,"F"))
r("R2","10R","R_0402","VSYS","INA1_INN",(8.0,14.0,0,"F"))
r("R3","10R","R_0402","SOL_RAW","INA2_INP",(16.5,10.2,0,"F"))
r("R4","10R","R_0402","SOL","INA2_INN",(16.5,14.2,0,"F"))
r("R5","2.2k","R_0402",V3,"I2C_SDA",(19.1,5.0,90,"F"))
r("R6","2.2k","R_0402",V3,"I2C_SCL",(21.1,5.0,90,"F"))
r("R7","1k","R_0402","BUZ","BUZ_G",(11.0,20.5,0,"F"))
r("R8","10k","R_0402",V3,"ESP_EN",(34.5,20.5,0,"F"))
r("R9","10k","R_0402",V3,"ESP_IO0",(37.0,20.5,0,"F"))
r("R10","10k","R_0402",V3,"GPS_RST",(21.0,20.6,90,"F"))
r("R11","100k","R_0402","Q2_G",G,(32.0,20.5,0,"F"))
r("R12","100k","R_0402","VSYS","BUCK_EN",(6.0,18.0,0,"F"))
add("R13","20mR 1W (shunt)","R","R_2512",[(1,"1","VBAT","L"),(2,"2","VSYS","R")],(20.1,11.8,90,"F"),"Battery shunt, INA228")
add("R14","1R 0.25W (shunt)","R","R_0805",[(1,"1","SOL_RAW","L"),(2,"2","SOL","R")],(17.0,16.8,90,"F"),"Solar shunt, INA226")
add("R15","100R 0.5W","R","R_1206",[(1,"1","SOL","L"),(2,"2",G,"R")],(24.5,20.5,0,"F"),"Solar cell load near MPP")
add("Q1","2N7002","NMOS","SOT-23",[(1,"G","BUZ_G","L"),(2,"S",G,"R"),(3,"D","BUZ_D","R")],(10.0,18.0,0,"F"),"Buzzer driver")
add("Q2","AO3401 (P-MOS)","PMOS","SOT-23",[(1,"G","Q2_G","L"),(2,"S","VBAT","R"),(3,"D","VBAT_RAW","R")],(28.7,20.3,0,"F"),"Reverse-battery protection")
add("D1","1N4148W","D","D_SOD-123",[(1,"K",V3,"L"),(2,"A","BUZ_D","R")],(14.3,19.4,0,"F"),"Buzzer flyback")
add("BZ1","SMD buzzer 5x5","BUZZER","BUZZER_SMD_5x5",[(1,"+",V3,"L"),(2,"-","BUZ_D","R")],(36.7,15.0,0,"F"),"5x5 mm SMD magnetic buzzer, PWM ~2.7 kHz")
add("J1","Battery 2S","CONN_2","JST_PH_B2B-PH-SM4-TB_Vertical",[(1,"+","VBAT_RAW","L"),(2,"-",G,"L")],(9.3,34.2,0,"F"),"JST B2B-PH-SM4-TB (top entry)")
add("J2","Solar cell","CONN_2","JST_PH_B2B-PH-SM4-TB_Vertical",[(1,"+","SOL_RAW","L"),(2,"-",G,"L")],(19.3,34.2,0,"F"),"JST B2B-PH-SM4-TB (top entry)")
add("J3","Arducam Mega","CONN_6","JST_SH_BM06B-SRSS-TB_Vertical",[(1,"VCC",V3,"L"),(2,"GND",G,"L"),(3,"SCK","SPI_SCK","L"),(4,"MISO","SPI_MISO","L"),(5,"MOSI","SPI_MOSI","L"),(6,"CS","CAM_CS","L")],(29.5,32.0,0,"F"),"JST BM06B-SRSS-TB")
add("J4","ESP32 prog","CONN_4","JST_SH_BM04B-SRSS-TB_Vertical",[(1,"3V3",V3,"L"),(2,"GND",G,"L"),(3,"ESP_TXD0","ESP_TX","L"),(4,"ESP_RXD0","ESP_RX","L")],(35.0,38.0,0,"F"),"Optional direct ESP32 UART (EN/IO0 come from Teensy D16/D17)")
add("J7","RBF / power","CONN_2","JST_SH_BM02B-SRSS-TB_Vertical",[(1,"EN","BUCK_EN","L"),(2,"GND",G,"L")],(27.6,38.0,0,"F"),"Short = both bucks off")
for i, n in enumerate([V3, V5, "VBAT_RAW", G, "SOL_RAW"]): add(f"PWR{i+1}", "PWR_FLAG", "PWR_FLAG", "", [(1, "pwr", n, "L")], None)

# ------------------------------------------------------------ Rev B placement (real courtyards)
POS = {
 "U8":(4.8,12.0,0,"F"),
 "R1":(9.0,10.0,0,"F"),
 "C13":(9.0,12.0,90,"F"),
 "R2":(9.0,14.0,0,"F"),
 "C10":(17.0,8.2,0,"F"),
 "C20":(23.2,8.3,0,"F"),
 "R13":(20.3,12.6,90,"F"),
 "C19":(23.6,18.6,90,"F"),
 "R10":(21.0,21.1,90,"F"),
 "R14":(16.8,16.8,90,"F"),
 "D1":(13.7,19.8,0,"F"),
 "R7":(10.2,20.6,0,"F"),
 "C18":(8.2,20.5,0,"F"),
 "C17":(5.4,20.5,0,"F"),
 "C16":(2.5,21.0,90,"F"),
 "C15":(2.5,17.0,90,"F"),
 "Q1":(9.6,17.8,0,"F"),
 "L2":(24.5,11.2,0,"F"),
 "C4":(23.6,15.2,90,"F"),
 "C23":(25.6,14.9,90,"F"),
 "BZ1":(30.2,15.6,0,"F"),
 "U12":(36.5,17.0,90,"F"),
 "R8":(7.0,40.0,0,"F"),
 "R9":(9.6,40.0,0,"F"),
 "C22":(12.2,40.0,0,"F"),
 "R11":(29.3,23.2,0,"F"),
 "C5":(35.2,5.6,90,"F"),
 "C6":(17.4,40.0,0,"F"),
 "U10":(23.2,5.6,0,"F"),
 "L1":(27.7,5.6,0,"F"),
 "U11":(32.3,5.6,0,"F"),
 "C2":(37.2,10.3,0,"F"),
 "C3":(33.4,10.3,0,"F"),
 "C1":(29.6,10.3,0,"F"),
 "R15":(24.6,21.5,0,"F"),
 "Q2":(28.9,20.5,0,"F"),
 "U4":(27.8,12.5,180,"B"),
 "J5":(37.6,18.0,0,"B"),
 "U3":(10.0,12.5,180,"B"),
 "R5":(18.6,5.0,90,"F"),
 "R6":(20.4,5.0,90,"F"),
 "R3":(17.4,10.2,0,"F"),
 "C14":(17.4,12.2,90,"F"),
 "R4":(17.4,14.2,0,"F"),
 "C11":(5.0,14.6,0,"F"),
 "U9":(13.2,12.0,0,"F"),
 "C12":(13.2,14.8,0,"F"),
}
for cm in COMP:
    if cm["ref"] in POS: cm["pcb"] = POS[cm["ref"]]

# ------------------------------------------------------------ geometry helpers / placement check
def rot_pt(x, y, rot):
    """KiCad rotation: CCW on screen with y pointing down."""
    a = math.radians(rot); return (x*math.cos(a) + y*math.sin(a), -x*math.sin(a) + y*math.cos(a))
def pad_world(cm, p):
    """World position and size of a pad as KiCad renders it (back-side footprints store y-mirrored pads)."""
    x, y, rot, side = cm["pcb"]; py = -p[4] if side == "B" else p[4]
    px, py = rot_pt(p[3], py, rot); w, h = p[5], p[6]
    if (rot + p[8]) % 180 == 90: w, h = h, w
    return x+px, y+py, w, h
def rect_rot(r, rot):
    pts = [rot_pt(px, py, rot) for px, py in [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; return (min(xs), min(ys), max(xs), max(ys))
def check():
    items = []
    for cm in COMP:
        if not cm["pcb"]: continue
        x, y, rot, side = cm["pcb"]; fpd = FP[cm["fp"]]
        for cr in (fpd.get("crtyd_list") or [fpd["crtyd"]]):
            if side == "B": cr = (cr[0], -cr[3], cr[2], -cr[1])
            a = rect_rot(cr, rot); items.append((cm["ref"], side, (x+a[0], y+a[1], x+a[2], y+a[3])))
        for p in fpd["pads"]:
            if p[1] != "thru_hole": continue
            cx, cy, w, h = pad_world(cm, p); rr = w/2
            items.append((cm["ref"]+"(hole)", "B" if side == "F" else "F", (cx-rr, cy-rr, cx+rr, cy+rr)))
    bad = set()
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            r1, s1, a = items[i]; r2, s2, b = items[j]
            if s1 != s2 or r1.split("(")[0] == r2.split("(")[0]: continue
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]: bad.add((r1, r2))
    out = [(rf, s, tuple(round(v, 2) for v in x)) for rf, s, x in items if (x[0] < 0 or x[1] < 0 or x[2] > BW or x[3] > BH) and "hole" not in rf]
    # pad-to-pad copper clearance across footprints on the same side
    pads = []
    for cm in COMP:
        if not cm["pcb"]: continue
        x, y, rot, side = cm["pcb"]; fpd = FP[cm["fp"]]; nm = {p[0]: p[2] for p in cm["pins"]}
        for p in fpd["pads"]:
            if p[10] and not any(l.endswith(".Cu") for l in p[10]): continue
            cx, cy, w, h = pad_world(cm, p)
            for sd in (["F", "B"] if p[1] == "thru_hole" else [side]): pads.append((cm["ref"], sd, nm.get(p[0]), (cx-w/2, cy-h/2, cx+w/2, cy+h/2)))
    viol = set()
    for i in range(len(pads)):
        for j in range(i+1, len(pads)):
            r1, s1, n1, a = pads[i]; r2, s2, n2, b = pads[j]
            if s1 != s2 or r1 == r2 or (n1 == n2 and n1): continue
            gap = max(b[0]-a[2], a[0]-b[2], b[1]-a[3], a[1]-b[3])
            if gap < 0.127: viol.add((r1, r2, round(gap, 3)))
    edge = [(rf, round(min(x[0], y0 := x[1], BW-x[2], BH-x[3]), 2)) for rf, s, n, x in pads if min(x[0], x[1], BW-x[2], BH-x[3]) < 0.5]
    return sorted(bad), out, sorted(viol), edge

# ------------------------------------------------------------ symbols + schematic (unchanged approach)
SYMS = {}
def build_symbol(name, pinlist):
    L = [p for p in pinlist if p[3] == "L"]; R = [p for p in pinlist if p[3] == "R"]
    rows = max(len(L), len(R)); longest = max([len(p[1]) for p in pinlist]+[len(name)])
    W = max(15.24, round((longest*1.4+6)/2.54)*2.54); H = (rows+1)*2.54; geo = {}
    for i, p in enumerate(L): geo[p[0]] = (-W/2-2.54, H/2-2.54*(i+1), 0)
    for i, p in enumerate(R): geo[p[0]] = (W/2+2.54, H/2-2.54*(i+1), 180)
    return dict(W=W, H=H, geo=geo, pins=pinlist)
for cm in COMP:
    if cm["sym"] not in SYMS: SYMS[cm["sym"]] = build_symbol(cm["sym"], cm["pins"])
def sym_sexpr(name, S, prefix=""):
    refp = name[0] if name in ("R","C","L","D","NMOS","PMOS","CONN_2","CONN_4","CONN_6","PWR_FLAG","BUZZER") else "U"
    lines = [f'  (symbol "{prefix}{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
      f'    (property "Reference" "{refp}" (at {-S["W"]/2:.2f} {S["H"]/2+1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))',
      f'    (property "Value" "{name}" (at {-S["W"]/2:.2f} {-S["H"]/2-1.27:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))',
      '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
      '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
      '    (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
      f'    (symbol "{name}_0_1" (rectangle (start {-S["W"]/2:.2f} {S["H"]/2:.2f}) (end {S["W"]/2:.2f} {-S["H"]/2:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))',
      f'    (symbol "{name}_1_1"']
    for p in S["pins"]:
        x, y, rot = S["geo"][p[0]]; ptype = "power_out" if name == "PWR_FLAG" else "passive"
        lines.append(f'      (pin {ptype} line (at {x:.2f} {y:.2f} {rot}) (length 2.54) (name "{p[1]}" (effects (font (size 1.27 1.27)))) (number "{p[0]}" (effects (font (size 1.27 1.27)))))')
    lines += ['    )', '  )']; return "\n".join(lines)

def write_schematic():
    sch = ['(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")', f'  (uuid "{ROOT_UUID}")', '  (paper "A2")', '  (lib_symbols']
    for n, S in SYMS.items(): sch.append(sym_sexpr(n, S, "cansat:"))
    sch.append('  )')
    cols = [30, 120, 210, 300, 390, 480]; colh = [20]*len(cols)
    for cm in sorted(COMP, key=lambda c_: -SYMS[c_["sym"]]["H"]):
        S = SYMS[cm["sym"]]; ci = min(range(len(cols)), key=lambda i: colh[i])
        X = cols[ci]; Y = round((colh[ci]+S["H"]/2)/1.27)*1.27; colh[ci] = Y+S["H"]/2+15
        cm["uuid"] = U()
        sch.append(f'  (symbol (lib_id "cansat:{cm["sym"]}") (at {X:.2f} {Y:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom {"no" if cm["sym"]=="PWR_FLAG" else "yes"}) (on_board yes) (dnp no) (uuid "{cm["uuid"]}")')
        sch.append(f'    (property "Reference" "{cm["ref"]}" (at {X-S["W"]/2:.2f} {Y-S["H"]/2-2.54:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
        sch.append(f'    (property "Value" "{cm["value"]}" (at {X-S["W"]/2:.2f} {Y+S["H"]/2+2.54:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')
        sch.append(f'    (property "Footprint" "{("cansat:"+cm["fp"]) if cm["fp"] else ""}" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        sch.append(f'    (property "Datasheet" "" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        sch.append(f'    (property "Description" "{cm["desc"]}" (at {X:.2f} {Y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        for p in cm["pins"]: sch.append(f'    (pin "{p[0]}" (uuid "{U()}"))')
        sch.append(f'    (instances (project "cansat" (path "/{ROOT_UUID}" (reference "{cm["ref"]}") (unit 1))))'); sch.append('  )')
        for p in cm["pins"]:
            if p[2] is None: continue
            px, py, rot = S["geo"][p[0]]; ax, ay = X+px, Y-py; lrot = 180 if rot == 0 else 0; just = "right" if rot == 0 else "left"
            sch.append(f'  (global_label "{p[2]}" (shape bidirectional) (at {ax:.2f} {ay:.2f} {lrot}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{U()}")')
            sch.append(f'    (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ax:.2f} {ay:.2f} 0) (effects (font (size 1.27 1.27)) (justify {just}) (hide yes))))')
    sch += ['  (sheet_instances (path "/" (page "1")))', ')']
    open(os.path.join(OUT, "cansat.kicad_sch"), "w", encoding="utf-8").write("\n".join(sch))
    lib = ['(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor") (generator_version "8.0")'] + [sym_sexpr(n, S) for n, S in SYMS.items()] + [')']
    open(os.path.join(LIB, "cansat.kicad_sym"), "w", encoding="utf-8").write("\n".join(lib))

# ------------------------------------------------------------ footprint emission (F/B aware)
def fp_lines(fpd, side, comp=None, rot=0.0, netid=None):
    sgn = -1 if side == "B" else 1
    def L(layer): return layer.replace("F.", f"{side}.") if layer.startswith("F.") else layer
    mirror = " (justify mirror)" if side == "B" else ""
    ref = comp["ref"] if comp else "REF**"; val = comp["value"] if comp else fpd["name"]
    fx0, fy0, fx1, fy1 = fpd["fab"]; big = fpd["src"] is None and min(fx1-fx0, fy1-fy0) >= 5.0 and any(g[1].endswith("SilkS") for g in fpd["gfx"])
    refy = 0 if big else sgn*(fy0-1.0)
    out = [f'    (property "Reference" "{ref}" (at 0 {refy:.2f} {rot}) (layer "{side}.SilkS" if big else "{side}.Fab") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12)){mirror}))'.replace('(layer "'+side+'.SilkS" if big else "'+side+'.Fab")', f'(layer "{side}.SilkS")' if big else f'(layer "{side}.Fab")'),
           f'    (property "Value" "{val}" (at 0 {sgn*(fy1+1.0):.2f} {rot}) (layer "{side}.Fab") (uuid "{U()}") (effects (font (size 0.6 0.6) (thickness 0.1)){mirror}))',
           f'    (property "Footprint" "cansat:{fpd["name"]}" (at 0 0 {rot}) (layer "{side}.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1.27 1.27))))',
           f'    (property "Datasheet" "" (at 0 0 {rot}) (layer "{side}.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1.27 1.27))))',
           f'    (property "Description" "{comp["desc"] if comp else ""}" (at 0 0 {rot}) (layer "{side}.Fab") (hide yes) (uuid "{U()}") (effects (font (size 1.27 1.27))))',
           f'    (attr {"through_hole" if fpd["pads"][0][1]=="thru_hole" else "smd"})']
    for t, layer, p in fpd["gfx"]:
        w = 0.05 if "CrtYd" in layer else (0.12 if "SilkS" in layer else 0.1)
        if t == "circle":
            out.append(f'    (fp_circle (center {p[0]:.3f} {sgn*p[1]:.3f}) (end {p[2]:.3f} {sgn*p[3]:.3f}) (stroke (width {w}) (type default)) (fill none) (layer "{L(layer)}") (uuid "{U()}"))')
        elif t == "rect":
            out.append(f'    (fp_rect (start {p[0]:.3f} {sgn*p[1]:.3f}) (end {p[2]:.3f} {sgn*p[3]:.3f}) (stroke (width {w}) (type default)) (fill none) (layer "{L(layer)}") (uuid "{U()}"))')
        else:
            out.append(f'    (fp_line (start {p[0]:.3f} {sgn*p[1]:.3f}) (end {p[2]:.3f} {sgn*p[3]:.3f}) (stroke (width {w}) (type default)) (layer "{L(layer)}") (uuid "{U()}"))')
    netmap = {p[0]: p[2] for p in comp["pins"]} if comp else {}
    for (pnum, kind, shape, x, y, w, h, drill, prot, rr, layers) in fpd["pads"]:
        y2 = sgn*y; r2 = (rot + prot) if side == "F" else (rot - prot)
        if kind == "smd":
            lay = " ".join(f'"{L(l)}"' for l in layers) if layers else f'"{side}.Cu" "{side}.Paste" "{side}.Mask"'
            s = f'    (pad "{pnum}" smd {shape} (at {x:.3f} {y2:.3f} {r2:g}) (size {w:.3f} {h:.3f}) (layers {lay})'
            if shape == "roundrect": s += f' (roundrect_rratio {rr:g})'
        else:
            s = f'    (pad "{pnum}" thru_hole {shape} (at {x:.3f} {y2:.3f} {r2:g}) (size {w:.3f} {h:.3f}) (drill {drill:g}) (layers "*.Cu" "*.Mask")'
        n = netmap.get(pnum)
        if n and netid: s += f' (net {netid[n]} "{n}")'
        out.append(s + f' (uuid "{U()}"))')
    return out

def write_pcb_and_lib(extra=None):
    nets = sorted({p[2] for cm in COMP for p in cm["pins"] if p[2]}); netid = {n: i+1 for i, n in enumerate(nets)}
    for n, fpd in FP.items():
        m = [f'(footprint "{n}" (version 20240108) (generator "pcbnew") (generator_version "8.0") (layer "F.Cu")'] + fp_lines(fpd, "F") + [')']
        open(os.path.join(PRETTY, n + ".kicad_mod"), "w", encoding="utf-8").write("\n".join(m))
    pcb = ['(kicad_pcb (version 20240108) (generator "pcbnew") (generator_version "8.0")', '  (general (thickness 1.6) (legacy_teardrops no))', '  (paper "A4")',
     '  (layers (0 "F.Cu" signal) (1 "In1.Cu" power) (2 "In2.Cu" power) (31 "B.Cu" signal) (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive") (34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments") (44 "Edge.Cuts" user) (45 "Margin" user) (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard") (48 "B.Fab" user) (49 "F.Fab" user))',
     '  (setup (stackup (layer "F.SilkS" (type "Top Silk Screen")) (layer "F.Paste" (type "Top Solder Paste")) (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01)) (layer "F.Cu" (type "copper") (thickness 0.035)) (layer "dielectric 1" (type "prepreg") (thickness 0.2104) (material "FR4") (epsilon_r 4.4) (loss_tangent 0.02)) (layer "In1.Cu" (type "copper") (thickness 0.0152)) (layer "dielectric 2" (type "core") (thickness 1.065) (material "FR4") (epsilon_r 4.4) (loss_tangent 0.02)) (layer "In2.Cu" (type "copper") (thickness 0.0152)) (layer "dielectric 3" (type "prepreg") (thickness 0.2104) (material "FR4") (epsilon_r 4.4) (loss_tangent 0.02)) (layer "B.Cu" (type "copper") (thickness 0.035)) (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01)) (layer "B.Paste" (type "Bottom Solder Paste")) (layer "B.SilkS" (type "Bottom Silk Screen")) (copper_finish "None") (dielectric_constraints no)) (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no) (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000) (disableapertmacros no) (usegerberextensions no) (usegerberattributes yes) (usegerberadvancedattributes yes) (creategerberjobfile yes) (dashed_line_dash_ratio 12.000000) (dashed_line_gap_ratio 3.000000) (svgprecision 4) (plotframeref no) (viasonmask no) (mode 1) (useauxorigin no) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15.000000) (pdf_front_fp_property_popups yes) (pdf_back_fp_property_popups yes) (dxfpolygonmode yes) (dxfimperialunits yes) (dxfusepcbnewfont yes) (psnegative no) (psa4output no) (plotreference yes) (plotvalue yes) (plotfptext yes) (plotinvisibletext no) (sketchpadsonfab no) (subtractmaskfromsilk no) (outputformat 1) (mirror no) (drillshape 1) (scaleselection 1) (outputdirectory "")))',
     '  (net 0 "")'] + [f'  (net {netid[n]} "{n}")' for n in nets]
    for cm in COMP:
        if not cm["pcb"]: continue
        x, y, rot, side = cm["pcb"]; fpd = FP[cm["fp"]]
        pcb.append(f'  (footprint "cansat:{fpd["name"]}" (layer "{side}.Cu") (uuid "{U()}") (at {x:.3f} {y:.3f} {rot})'); pcb.append(f'    (path "/{cm["uuid"]}")')
        pcb += fp_lines(fpd, side, cm, rot, netid); pcb.append('  )')
    for (x1, y1, x2, y2) in [(0, 0, BW, 0), (BW, 0, BW, BH), (BW, BH, 0, BH), (0, BH, 0, 0)]:
        pcb.append(f'  (gr_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (uuid "{U()}"))')
    pcb.append(f'  (gr_text "CanSat carrier Rev C  40x45  4-layer" (at 20 -2 0) (layer "Cmts.User") (uuid "{U()}") (effects (font (size 1.5 1.5) (thickness 0.2))))')
    if extra: pcb += extra
    pcb.append(')')
    open(os.path.join(OUT, "cansat.kicad_pcb"), "w", encoding="utf-8").write("\n".join(pcb))
    pro = {"board":{"design_settings":{"defaults":{},"rules":{"min_clearance":0.127,"min_track_width":0.15,"min_via_diameter":0.4,"min_via_annular_width":0.1,"min_through_hole_diameter":0.2,"min_hole_to_hole":0.25,"min_hole_clearance":0.2,"min_copper_edge_clearance":0.4,"min_resolved_spokes":1,"min_silk_clearance":0.0,"solder_mask_min_width":0.0,"solder_mask_to_copper_clearance":0.0}}},
     "boards":[],"cvpcb":{"equivalence_files":[]},"libraries":{"pinned_footprint_libs":[],"pinned_symbol_libs":[]},"meta":{"filename":"cansat.kicad_pro","version":1},
     "net_settings":{"classes":[{"name":"Default","clearance":0.127,"track_width":0.2,"via_diameter":0.5,"via_drill":0.25,"microvia_diameter":0.3,"microvia_drill":0.1,"diff_pair_width":0.2,"diff_pair_gap":0.25,"diff_pair_via_gap":0.25,"line_style":0,"wire_width":6,"bus_width":12,"pcb_color":"rgba(0, 0, 0, 0.000)","schematic_color":"rgba(0, 0, 0, 0.000)"}],"meta":{"version":3},"net_colors":None,"netclass_assignments":None,"netclass_patterns":[]},
     "pcbnew":{"last_paths":{"gencad":"","idf":"","netlist":"","plot":"","pos_files":"","specctra_dsn":"","step":"","svg":"","vrml":""},"page_layout_descr_file":""},
     "schematic":{"legacy_lib_dir":"","legacy_lib_list":[]},"sheets":[[ROOT_UUID,"Root"]],"text_variables":{}}
    json.dump(pro, open(os.path.join(OUT, "cansat.kicad_pro"), "w"), indent=2)
    open(os.path.join(OUT, "sym-lib-table"), "w").write('(sym_lib_table (version 7)\n  (lib (name "cansat")(type "KiCad")(uri "${KIPRJMOD}/lib/cansat.kicad_sym")(options "")(descr "CanSat project symbols"))\n)\n')
    open(os.path.join(OUT, "fp-lib-table"), "w").write('(fp_lib_table (version 7)\n  (lib (name "cansat")(type "KiCad")(uri "${KIPRJMOD}/lib/cansat.pretty")(options "")(descr "CanSat project footprints"))\n)\n')
    with open(os.path.join(OUT, "bom.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["Ref", "Value", "Footprint", "Source", "Side", "X(mm)", "Y(mm)", "Rot", "Note"])
        for cm in COMP:
            if not cm["pcb"]: continue
            x, y, rot, side = cm["pcb"]; w.writerow([cm["ref"], cm["value"], cm["fp"], FP[cm["fp"]]["src"] or "datasheet", side, x, y, rot, cm["desc"]])

NETS = sorted({p[2] for cm in COMP for p in cm["pins"] if p[2]}); NETID = {n: i+1 for i, n in enumerate(NETS)}
if __name__ == "__main__":
    import sys
    bad, outside, viol, edge = check()
    print("courtyard overlaps:", bad); print("outside board:", outside); print("pad clearance <0.127:", viol); print("copper <0.5 from edge:", edge)
    if "--write" in sys.argv:
        write_schematic(); write_pcb_and_lib(); print("written:", len([c_ for c_ in COMP if c_["pcb"]]), "parts")

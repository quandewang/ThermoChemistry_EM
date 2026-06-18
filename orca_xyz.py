import os
import re

# ====================== 【用户配置】 ======================
INPUT_FOLDER = r"D:\Energetic Materials\Molecular_Structures\ThermoDatabase\Orca_Opt_Freq\OptFreq"
# 提取后的 xyz 文件保存到这里（自动创建）
OUTPUT_FOLDER = r"D:\Energetic Materials\Molecular_Structures\ThermoDatabase\Orca_Opt_Freq\OptFreq\xyzfile"
# =========================================================

def extract_final_xyz(log_path):
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    # 只匹配：FINAL ENERGY 后面的 CARTESIAN COORDINATES (ANGSTROEM)
    target_found = False
    coords = []

    for line in lines:
        line = line.strip()

        # 1. 找到最终能量区域 → 准备读取坐标
        if "FINAL ENERGY EVALUATION AT THE STATIONARY POINT" in line:
            target_found = True

        # 2. 找到目标坐标块
        if target_found and "CARTESIAN COORDINATES (ANGSTROEM)" in line:
            # 清空，开始读取
            coords = []
            continue

        # 3. 停止条件：遇到下一个坐标块（A.U.）
        if target_found and "CARTESIAN COORDINATES (A.U.)" in line:
            break

        # 4. 读取原子行（严格匹配你的格式）
        if target_found and coords is not None:
            match = re.match(r'^([A-Za-z]+)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)$', line)
            if match:
                elem = match.group(1)
                x = match.group(2)
                y = match.group(3)
                z = match.group(4)
                coords.append(f"{elem:2} {x:>15} {y:>15} {z:>15}")

    if not coords:
        return None

    # 输出标准 XYZ
    xyz = f"{len(coords)}\n\n" + "\n".join(coords)
    return xyz

def batch_extract():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    logs = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".log")]

    print("=" * 60)
    print(" ORCA 6.0 最终优化结构 → XYZ 提取【精准版】")
    print("=" * 60)

    ok = 0
    no = 0

    for f in logs:
        name = os.path.splitext(f)[0]
        path = os.path.join(INPUT_FOLDER, f)
        xyz = extract_final_xyz(path)

        if xyz:
            out = os.path.join(OUTPUT_FOLDER, name + ".xyz")
            with open(out, 'w', encoding='utf-8') as f_out:
                f_out.write(xyz)
            print(f"✅ {name}.xyz 提取成功")
            ok +=1
        else:
            print(f"❌ {f} 未找到最终坐标")
            no +=1

    print("-"*60)
    print(f"✅ 成功：{ok} 个")
    print(f"❌ 失败：{no} 个")
    print("🎉 全部完成！")

if __name__ == "__main__":
    batch_extract()
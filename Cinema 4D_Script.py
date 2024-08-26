import c4d
from c4d import gui
import os
import shutil

def update_counter_file(export_folder, counter):
    counter_file_path = os.path.join(export_folder, 'counter.txt')
    with open(counter_file_path, 'w') as file:
        file.write(str(counter))  # 正确转换 counter 为字符串

def get_next_counter(export_folder):
    counter_file_path = os.path.join(export_folder, 'counter.txt')

    try:
        # 尝试读取计数器文件中的当前计数
        if os.path.exists(counter_file_path):
            with open(counter_file_path, 'r') as file:
                return int(file.read().strip())
        else:
            return 1  # 如果文件不存在，则从1开始
    except ValueError:
        # 如果文件内容不是整数，则从1开始
        return 1

def lerp_color(color1, color2, t):
    """Linearly interpolate between two colors."""
    return [int(color1[i] * (1 - t) + color2[i] * t) for i in range(3)]

def GradientToBitmap(gradient, width, height, gradient_type):
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        return None

    bmp.Init(width, height)

    knot_count = gradient.GetKnotCount()
    if (knot_count == 0):
        return None

    knots = sorted([gradient.GetKnot(i) for i in range(knot_count)], key=lambda k: k["pos"])

    for x in range(width):
        for y in range(height):
            if gradient_type in [c4d.SLA_GRADIENT_TYPE_2D_U, c4d.SLA_GRADIENT_TYPE_2D_V]:
                t = float(x) if gradient_type == c4d.SLA_GRADIENT_TYPE_2D_U else float(y)
                t /= (width - 1)

            # Determine the color for the given t value
            if t <= knots[0]["pos"]:
                color = [int(knots[0]["col"][j] * 255) for j in range(3)]
            elif t >= knots[-1]["pos"]:
                color = [int(knots[-1]["col"][j] * 255) for j in range(3)]
            else:
                for i in range(knot_count - 1):
                    if knots[i]["pos"] <= t <= knots[i + 1]["pos"]:
                        lerp_factor = (t - knots[i]["pos"]) / (knots[i + 1]["pos"] - knots[i]["pos"])
                        color = lerp_color(
                            [knots[i]["col"][j] * 255 for j in range(3)],
                            [knots[i + 1]["col"][j] * 255 for j in range(3)],
                            lerp_factor
                        )
                        break

            bmp.SetPixel(x, y, *color)

    return bmp

def generate_unique_name_and_update(base_name, obj):
    """Generate a unique name and update the object name if necessary."""
    name = base_name

    # Construct the platform-independent path to the "Documents" directory
    documents_path = os.path.expanduser('~/Documents')

    # Only change name if file exists
    if os.path.exists(os.path.join(documents_path, f"{name}_preview.jpg")):
        counter = 1
        name = f"{base_name}_{str(counter).zfill(3)}"

        while os.path.exists(os.path.join(documents_path, f"{name}_preview.jpg")):
            counter += 1
            name = f"{base_name}_{str(counter).zfill(3)}"

        # Update the object's name if it was changed
        obj.SetName(name)

    return name

def GetGradientFromOctaneLightTagAndPrint():
    doc = c4d.documents.GetActiveDocument()
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

    for obj in selected_objects:
        tags = obj.GetTags()
        for tag in tags:
            if tag.GetTypeName() == "Octane LightTag":
                shader = tag[c4d.LIGHTTAG_EFFIC_OR_TEX]
                if shader is not None:
                    gradient_data = shader[c4d.SLA_GRADIENT_GRADIENT]
                    gradient_type = shader[c4d.SLA_GRADIENT_TYPE]  # Get the gradient type

                    if gradient_data is not None:
                        # Print knot info to the console
                        for i in range(gradient_data.GetKnotCount()):
                            knot = gradient_data.GetKnot(i)
                            print(f"Knot {i + 1}:")
                            print(f"Position: {knot['pos'] * 100}%")
                            print(f"Color: RGB({knot['col'].x}, {knot['col'].y}, {knot['col'].z})")
                            print("-----")

                        bmp = GradientToBitmap(gradient_data, 256, 256, gradient_type)  # Pass the gradient type
                        if bmp is not None:
                            unique_name = generate_unique_name_and_update(obj.GetName(), obj)
                            # Construct the platform-independent path to save the gradient preview
                            output_path = os.path.join(os.path.expanduser('~/Documents'), f"{unique_name}.jpg")
                            bmp.Save(output_path, c4d.FILTER_JPG)
                            print(f"Saved gradient preview to: {output_path}")

def ExportOctaneLightTagImages():
    doc = c4d.documents.GetActiveDocument()
    selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)

    documents_path = os.path.expanduser('~/Documents')

    # 确保目标文件夹存在
    if not os.path.exists(documents_path):
        os.makedirs(documents_path)

    for obj in selected_objects:
        tags = obj.GetTags()
        for tag in tags:
            if tag.GetTypeName() == "Octane LightTag":
                texture_shader = tag[c4d.LIGHTTAG_EFFIC_OR_TEX]
                if texture_shader is not None:
                    if texture_shader.CheckType(c4d.Xbitmap):  # 标准位图着色器
                        image_path = texture_shader[c4d.BITMAPSHADER_FILENAME]
                        if image_path and os.path.exists(image_path):
                            light_name = obj[c4d.ID_BASELIST_NAME]
                            file_extension = os.path.splitext(image_path)[1]
                            destination_file_name = light_name + file_extension
                            destination_path = os.path.join(documents_path, destination_file_name)
                            shutil.copy(image_path, destination_path)
                            print(f"Image exported: {destination_path}")
                    elif texture_shader.CheckType(1029508):  # Octane Image Texture
                        image_path = texture_shader[c4d.IMAGETEXTURE_FILE]
                        if image_path and os.path.exists(image_path):
                            light_name = obj[c4d.ID_BASELIST_NAME]
                            file_extension = os.path.splitext(image_path)[1]
                            destination_file_name = light_name + file_extension
                            destination_path = os.path.join(documents_path, destination_file_name)
                            shutil.copy(image_path, destination_path)
                            print(f"Image exported: {destination_path}")
                    elif texture_shader.CheckType(c4d.Xcolor):  # 颜色着色器
                        color = texture_shader[c4d.COLORSHADER_COLOR]
                        r, g, b = int(color.x * 255), int(color.y * 255), int(color.z * 255)
                        bmp = c4d.bitmaps.BaseBitmap()
                        bmp.Init(64, 64, depth=24)
                        for y in range(64):
                            for x in range(64):
                                bmp.SetPixel(x, y, r, g, b)

                        destination_file_name = obj[c4d.ID_BASELIST_NAME] + ".jpg"
                        destination_path = os.path.join(documents_path, destination_file_name)
                        bmp.Save(destination_path, c4d.FILTER_JPG)  # 保存为JPEG

def export_usd_lights_to_tmp():

    documents_path = os.path.expanduser('~/Documents')

    counter = get_next_counter(documents_path)

    export_path = os.path.join(documents_path, f"lights{counter}.usdc")

    # 获取当前文档
    doc = c4d.documents.GetActiveDocument()

    # 创建一个新的空文档
    new_doc = c4d.documents.BaseDocument()

    # 遍历当前文档的所有对象，查找灯光对象并复制到新文档中
    for obj in doc.GetObjects():
        if obj.GetType() == c4d.Olight:
            new_doc.InsertObject(obj.GetClone())

    # 设置导出路径

    if not os.path.exists(documents_path):
        os.makedirs(documents_path)

    # 计算文件名
    counter = get_next_counter(documents_path)
    export_path = os.path.join(documents_path, f"lights{counter}.usdc")
    while os.path.exists(export_path):
        counter += 1
        export_path = os.path.join(documents_path, f"lights{counter}.usdc")

    # 设置导出参数
    settings = c4d.BaseContainer()
    settings[c4d.USDEXPORTER_FILEFORMAT] = c4d.USDEXPORTER_FILEFORMAT_USDA
    settings[c4d.USDEXPORTER_EXPORT2LAYER] = True
    settings[c4d.USDEXPORTER_ZIP] = False
    settings[c4d.USDEXPORTER_CAMERAS] = False
    settings[c4d.USDEXPORTER_LIGHTUNITS] = c4d.USDEXPORTER_LIGHTUNITS_NIT
    settings[c4d.USDEXPORTER_GEOMETRY] = False
    settings[c4d.USDEXPORTER_NORMALS] = False
    settings[c4d.USDEXPORTER_UV] = False
    settings[c4d.USDEXPORTER_VERTEXCOLORS] = False
    settings[c4d.USDEXPORTER_DISPLAYCOLOR] = False
    settings[c4d.USDEXPORTER_MATERIALS] = c4d.USDEXPORTER_MATERIALS_NONE
    settings[c4d.USDEXPORTER_MATERIALS_BAKETEXTURES] = False

    # 执行导出
    result = c4d.documents.SaveDocument(new_doc, export_path, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, c4d.FORMAT_USDEXPORT)

    if result:
        print("导出成功!")
        update_counter_file(documents_path, counter + 1)
    else:
        print("导出失败.")

if __name__ == '__main__':
    GetGradientFromOctaneLightTagAndPrint()
    ExportOctaneLightTagImages()
    export_usd_lights_to_tmp()
    c4d.EventAdd()

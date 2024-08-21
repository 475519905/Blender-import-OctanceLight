import bpy
import os

bl_info = {
    "name": "Import Octance Lights",
    "blender": (3, 64, 0),
    "category": "Object",
}

def get_script_run_count():
    counter_file_path = os.path.join(os.path.expanduser('~'), 'Documents', 'counter.txt')
    if os.path.exists(counter_file_path):
        with open(counter_file_path, 'r') as file:
            counter = int(file.read().strip())
    else:
        counter = 0
    return counter - 1

def update_script_run_count():
    counter_file_path = os.path.join(os.path.expanduser('~'), 'Documents', 'counter.txt')
    current_count = get_script_run_count() + 1
    with open(counter_file_path, 'w') as file:
        file.write(str(current_count + 1))

def link_texture_to_light_from_folder(folder_path):
    extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    for light in bpy.data.lights:
        image_path = None
        for ext in extensions:
            potential_path = os.path.join(folder_path, light.name + ext)
            if os.path.exists(potential_path):
                image_path = potential_path
                break
        if image_path:
            # Enable use of nodes for this light data block
            light.use_nodes = True
            nodes = light.node_tree.nodes
            nodes.clear()  # Clear existing nodes
            
            # Create necessary nodes
            geom_node = nodes.new(type='ShaderNodeNewGeometry')
            mapping_node = nodes.new(type='ShaderNodeMapping')
            texture_node = nodes.new(type='ShaderNodeTexImage')
            emission_node = nodes.new(type='ShaderNodeEmission')
            output_node = nodes.new(type='ShaderNodeOutputLight')
            
            # Load and assign the image to the texture node
            image = bpy.data.images.load(image_path)
            texture_node.image = image
            
            # Set up node locations (for a cleaner layout)
            geom_node.location = (-600, 0)
            mapping_node.location = (-400, 0)
            texture_node.location = (-200, 0)
            emission_node.location = (0, 0)
            output_node.location = (200, 0)
            
            # Link the nodes together
            links = light.node_tree.links
            links.new(geom_node.outputs['Parametric'], mapping_node.inputs['Vector'])
            links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
            links.new(texture_node.outputs['Color'], emission_node.inputs['Color'])
            links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

            # 清除未使用的数据块
            for block in bpy.data.meshes:
                if block.users == 0:
                    bpy.data.meshes.remove(block)

            for block in bpy.data.materials:
                if block.users == 0:
                    bpy.data.materials.remove(block)
                    
            imported_objects = [obj for obj in bpy.context.selected_objects]

def import_and_delete_usd(filepath, scale_factor):
    global script_run_count
    try:
        # 导入 USD 文件
        bpy.ops.wm.usd_import(filepath=filepath, scale=scale_factor)
        print("USD文件导入成功!")
        
        # 删除与 USD 文件关联的所有对象
        imported_objects = [obj for obj in bpy.context.selected_objects]
                
        # 删除文件
        os.remove(filepath)
        update_script_run_count()
        print(f"已成功删除 {filepath} 文件!")
    except Exception as e:
        print(f"导入或删除文件时出错: {e}")
    finally:
        # 在函数末尾递增 run_count
        script_run_count += 1

# 设置文件路径和其他参数
script_run_count = get_script_run_count()

# 使用系统文档路径
doc_path = os.path.join(os.path.expanduser('~'), 'Documents')
usd_filepath = os.path.join(doc_path, f"lights{script_run_count}.usdc")
scale = 0.01
folder_path = doc_path

class OBJECT_OT_CustomOperator(bpy.types.Operator):
    bl_idname = "object.custom_operator"
    bl_label = "Import Octance Lights"

    def execute(self, context):
        script_run_count = get_script_run_count()
        
        # 使用系统文档路径
        doc_path = os.path.join(os.path.expanduser('~'), 'Documents')
        usd_filepath = os.path.join(doc_path, f"lights{script_run_count}.usdc")
        scale = 0.01
        folder_path = doc_path

        import_and_delete_usd(usd_filepath, scale)
        link_texture_to_light_from_folder(folder_path)

        return {'FINISHED'}

class OBJECT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Python Script"
    bl_idname = "OBJECT_PT_custom"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.custom_operator")

def register():
    bpy.utils.register_class(OBJECT_OT_CustomOperator)
    bpy.utils.register_class(OBJECT_PT_CustomPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CustomOperator)
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)

if __name__ == "__main__":
    register()

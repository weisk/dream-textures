import bpy
from bpy.props import CollectionProperty
from bpy_extras.io_utils import ImportHelper
import os
import webbrowser
import shutil

from .absolute_path import WEIGHTS_PATH, absolute_path
from .operators.install_dependencies import InstallDependencies
from .operators.open_latest_version import OpenLatestVersion
from .property_groups.dream_prompt import DreamPrompt

class OpenHuggingFace(bpy.types.Operator):
    bl_idname = "stable_diffusion.open_hugging_face"
    bl_label = "Download Weights from Hugging Face"
    bl_description = ("Opens huggingface.co to the download page for the model weights.")
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        webbrowser.open("https://huggingface.co/CompVis/stable-diffusion-v-1-4-original")
        return {"FINISHED"}

class OpenGitDownloads(bpy.types.Operator):
    bl_idname = "stable_diffusion.open_git_downloads"
    bl_label = "Go to git-scm.com"
    bl_description = ("Opens git-scm.com to the download page for Git")
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        webbrowser.open("https://git-scm.com/downloads")
        return {"FINISHED"}

class OpenWeightsDirectory(bpy.types.Operator, ImportHelper):
    bl_idname = "stable_diffusion.open_weights_directory"
    bl_label = "Import Model Weights"
    filename_ext = ".ckpt"
    filter_glob: bpy.props.StringProperty(
        default="*.ckpt",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        path = os.path.dirname(WEIGHTS_PATH)
        # if not os.path.exists(path):
        #     os.mkdir(path)
        # webbrowser.open(f"file:///{os.path.realpath(path)}")
        _, extension = os.path.splitext(self.filepath)
        if extension != '.ckpt':
            self.report({"ERROR"}, "Select a valid stable diffusion '.ckpt' file.")
            return {"FINISHED"}
        shutil.copy(self.filepath, WEIGHTS_PATH)
        
        return {"FINISHED"}

is_install_valid = None

class OpenRustInstaller(bpy.types.Operator):
    bl_idname = "stable_diffusion.open_rust_installer"
    bl_label = "Go to rust-lang.org"
    bl_description = ("Opens rust-lang.org to the install page")
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        webbrowser.open("https://www.rust-lang.org/tools/install")
        return {"FINISHED"}

class ValidateInstallation(bpy.types.Operator):
    bl_idname = "stable_diffusion.validate_installation"
    bl_label = "Validate Installation"
    bl_description = ("Tests importing the generator to locate a subset of errors with the installation")
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        global is_install_valid
        try:
            # Support Apple Silicon GPUs as much as possible.
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            from .stable_diffusion.ldm.generate import Generate
            
            is_install_valid = True
        except Exception as e:
            self.report({"ERROR"}, str(e))
            is_install_valid = False

        return {"FINISHED"}

class StableDiffusionPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    history: CollectionProperty(type=DreamPrompt)

    def draw(self, context):
        layout = self.layout

        weights_installed = os.path.exists(WEIGHTS_PATH)

        if not weights_installed:
            layout.label(text="Complete the following steps to finish setting up the addon:")

        if not os.path.exists(absolute_path("stable_diffusion")) or len(os.listdir(absolute_path("stable_diffusion"))) < 5:
            missing_sd_box = layout.box()
            missing_sd_box.label(text="Stable diffusion is missing.", icon="ERROR")
            missing_sd_box.label(text="You've likely downloaded source instead of release by accident.")
            missing_sd_box.operator(OpenLatestVersion.bl_idname, text="Download Latest Release")
            return
        else:
            dependencies_box = layout.box()
            dependencies_box.label(text="Dependencies Located", icon="CHECKMARK")
            dependencies_box.label(text="All dependencies (except for model weights) are included in the release.")

        model_weights_box = layout.box()
        model_weights_box.label(text="Setup Model Weights", icon="SETTINGS")
        if weights_installed:
            model_weights_box.label(text="Model weights setup successfully.", icon="CHECKMARK")
        else:
            model_weights_box.label(text="The model weights are not distributed with the addon.")
            model_weights_box.label(text="Follow the steps below to download and install them.")
            model_weights_box.label(text="1. Download the file 'sd-v1-4.ckpt'")
            model_weights_box.operator(OpenHuggingFace.bl_idname, icon="URL")
            model_weights_box.label(text="2. Select the downloaded weights to install.")
            model_weights_box.operator(OpenWeightsDirectory.bl_idname, text="Import Model Weights", icon="IMPORT")

        if weights_installed:
            complete_box = layout.box()
            complete_box.label(text="Addon Setup Complete", icon="CHECKMARK")
            complete_box.label(text="To locate the interface:")
            complete_box.label(text="1. Open an Image Editor or Shader Editor space")
            complete_box.label(text="2. Enable 'View' > 'Sidebar'")
            complete_box.label(text="3. Select the 'Dream' tab")

        if context.preferences.view.show_developer_ui: # If 'Developer Extras' is enabled, show addon development tools
            developer_box = layout.box()
            developer_box.label(text="Development Tools", icon="CONSOLE")
            developer_box.label(text="This section is for addon development only. You are seeing this because you have 'Developer Extras' enabled.")
            developer_box.label(text="Do not use any operators in this section unless you are setting up a development environment.")
            developer_box.prop(context.scene, 'dream_textures_requirements_path')
            developer_box.operator(InstallDependencies.bl_idname, icon="CONSOLE")
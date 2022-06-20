using FN_Engine;
using Microsoft.Xna.Framework;
using ImGuiNET;
using System;
using Microsoft.Xna.Framework.Graphics;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.IO;
using System.Diagnostics;

namespace GP
{
    public class Importer : GameObjectComponent
    {
        private Texture2D tex;
        private IntPtr texPointer;
        private string imagePath;
        private string videoPath;
        private string projDirectory;
        private int frameSamplingRate = 6;
        private int percentage = 0;
        private string currentOperation = "Nothing";

        public enum SampleRate { Four=4, Six=6, Nine=9};

        public override void Start()
        {
            tex = Setup.Content.Load<Texture2D>("Assets\\Logo");
            texPointer = Scene.GuiRenderer.BindTexture(tex);
            imagePath = "None";
            videoPath = "None";

            string currentDirectory = Directory.GetCurrentDirectory();
            projDirectory = currentDirectory.Remove(currentDirectory.LastIndexOf('\\'));
            projDirectory = projDirectory.Remove(projDirectory.LastIndexOf('\\'));
            projDirectory += "\\RiggingAndAnimation";
        }

        public override void Update(GameTime gameTime)
        {

        }

        public override void DrawUI()
        {
            ImGui.Begin("Modemation");

            float screenWidth = ImGui.GetWindowContentRegionWidth();
            float screenHeight = ImGui.GetWindowHeight();
            ImGui.Indent((screenWidth - tex.Width) * 0.5f);
            ImGui.Image(texPointer, new System.Numerics.Vector2(tex.Width, tex.Height));
            ImGui.Unindent(screenWidth * 0.45f);

            //Import input image
            if (ImGui.Button("Import Image", new System.Numerics.Vector2(screenWidth * 0.25f, 0)))
            {
                using (var fbd = new OpenFileDialog())
                {
                    DialogResult result = fbd.ShowDialog();

                    if (result == DialogResult.OK && !string.IsNullOrWhiteSpace(fbd.FileName))
                    {
                        imagePath = fbd.FileName;
                        string fileName = imagePath.Substring(imagePath.LastIndexOf('\\') + 1);

                        //Delete input image directory
                        if (Directory.Exists(projDirectory + "\\inputs\\image"))
                            Directory.Delete(projDirectory + "\\inputs\\image", true);

                        Directory.CreateDirectory(projDirectory + "\\inputs\\image");

                        //Copy image to project
                        File.Copy(imagePath, projDirectory + "\\inputs\\image" + "\\" + fileName);
                    }
                }
            }

            ImGui.SameLine();
            HelpMarker("Import input image with a T pose");

            //Import input video
            if (ImGui.Button("Import Video", new System.Numerics.Vector2(screenWidth * 0.25f, 0)))
            {
                using (var fbd = new OpenFileDialog())
                {
                    DialogResult result = fbd.ShowDialog();

                    if (result == DialogResult.OK && !string.IsNullOrWhiteSpace(fbd.FileName))
                    {
                        videoPath = fbd.FileName;
                        string fileName = videoPath.Substring(videoPath.LastIndexOf('\\') + 1);

                        //Delete input video directory
                        if (Directory.Exists(projDirectory + "\\inputs\\video"))
                            Directory.Delete(projDirectory + "\\inputs\\video", true);

                        Directory.CreateDirectory(projDirectory + "\\inputs\\video");

                        //Copy video to project
                        File.Copy(videoPath, projDirectory + "\\inputs\\video" + "\\" + fileName);
                    }
                }
            }

            ImGui.SameLine();
            HelpMarker("Import input video having a one character in it");

            if (ImGui.BeginCombo("Sampling Rate", frameSamplingRate.ToString()))
            {
                foreach (int val in Enum.GetValues(typeof(SampleRate)))
                    if (ImGui.Selectable(val.ToString()))
                        frameSamplingRate = val;

                ImGui.EndCombo();
            }

            ImGui.NewLine();
            ImGui.Separator();
            ImGui.NewLine();

            ImGui.SetCursorPosX(screenWidth * 0.43f);
            ImGui.Text("Current Operation: " + currentOperation);
            ImGui.SetCursorPosX(screenWidth * 0.43f);
            ImGui.Text("Progress: " + percentage.ToString() + "%");

            ImGui.SetCursorPosX(screenWidth * 0.5f - screenWidth * 0.125f);
            ImGui.SetCursorPosY(screenHeight * 0.75f);
            if (ImGui.Button("Start", new System.Numerics.Vector2(screenWidth * 0.25f, 0)))
            {
                if (Directory.Exists(projDirectory + "\\inputs\\video") &&
                    Directory.Exists(projDirectory + "\\inputs\\image") &&
                    Directory.GetFiles(projDirectory + "\\inputs\\video").Length != 0 &&
                    Directory.GetFiles(projDirectory + "\\inputs\\image").Length != 0)
                {
                    Threader.Invoke(StartOperation, 0);
                }
            }

            ImGui.End();
        }

        public static void HelpMarker(string desc, bool DisplayMarker = true)
        {
            if (DisplayMarker)
                ImGui.TextDisabled("(?)");
            if (ImGui.IsItemHovered())
            {
                ImGui.BeginTooltip();
                ImGui.PushTextWrapPos(ImGui.GetFontSize() * 35.0f);
                ImGui.TextUnformatted(desc);
                ImGui.PopTextWrapPos();
                ImGui.EndTooltip();
            }
        }

        void StartOperation()
        {
            currentOperation = "Image Preprocessing...";
            string[] imagePreprocessing = new string[]
            {
                "cd " + projDirectory, //Go to the existing directory
                "timeout 10",
                "py preprocessing/clear_dir.py",
                "py preprocessing/get_image.py ",
                "cd HumanSeg",
                "py bg_replace.py --config export_model/deeplabv3p_resnet50_os8_humanseg_512x512_100k_with_softmax/deploy.yaml --img_path data/human.jpg",
                "cd output",
                "move human.png ..",
                "cd ..",
                "move human.png ..",
                "cd ..",
                "move human.png frames",
                "cd frames",
                "move human.png initial",
                "cd ..",
                "py preprocessing/crop_image_1.py"
            };

            ExecuteCommand(imagePreprocessing, projDirectory);

            percentage = 5;
            
            //////////////////////////////////////////
            currentOperation = "Pose Estimation...";
            string[] poseEstimation = new string[]
            {
                "cd " + projDirectory, //Go to the existing directory
                "py preprocessing/get_frames.py -mfps " + frameSamplingRate.ToString() + " -rf 4",
                "move frames openpose",
                "cd openpose",
                "bin\\OpenPoseDemo.exe --image_dir frames/ --write_json frames/pose/",
                "bin\\OpenPoseDemo.exe --image_dir frames/initial/ --face --write_json frames/initial/",
                "move frames ..",
                "cd .."
            };

            Utility.ExecuteCommand(poseEstimation, projDirectory);

            percentage = 65;

            //////////////////////////////////////////
            currentOperation = "Cropping Input Image...";
            string[] croppingImage = new string[]
            {
                "cd " + projDirectory, //Go to the existing directory
                "py preprocessing/crop_image_2.py",
                "py preprocessing/get_proportions.py -out_dir human_proportions.json -s"
            };

            Utility.ExecuteCommand(croppingImage, projDirectory);

            percentage = 70;

            //////////////////////////////////////////
            currentOperation = "Building Model...";
            string[] buildingModel = new string[]
            {
                "cd " + projDirectory, //Go to the existing directory
                "move human_proportions.json ..",
                "cd ..",
                "move human_proportions.json Human3D",
                "cd Human3D",
                "move human_proportions.json data",
                ".\\build\\Debug\\fitting models/pcaModel_male.csv models/meanMesh.csv data/referenceObj.obj data/ids_index_v2.json data/human_proportions.json model_output/mesh.obj model_output/rigInfo.json",
                "move model_output ..",
                "cd ..",
                "move model_output \"RiggingAndAnimation\"",
                "cd \"RiggingAndAnimation\""
            };

            Utility.ExecuteCommand(buildingModel, projDirectory);

            percentage = 100;
        }

        public static void ExecuteCommand(string[] Commands, string Path)
        {
            string batFileName = Path + @"\" + Guid.NewGuid() + ".bat";

            using (StreamWriter batFile = new StreamWriter(batFileName))
            {
                foreach (string Comm in Commands)
                    batFile.WriteLine(Comm);
            }

            ProcessStartInfo processStartInfo = new ProcessStartInfo("cmd.exe", "/c " + batFileName);
            processStartInfo.UseShellExecute = false;
            processStartInfo.CreateNoWindow = false;
            processStartInfo.WindowStyle = ProcessWindowStyle.Normal;

            Process p = new Process();
            p.StartInfo = processStartInfo;
            p.Start();
            p.WaitForExit();

            File.Delete(batFileName);
        }
    }
}

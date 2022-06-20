using FN_Engine;
using Microsoft.Xna.Framework;
using ImGuiNET;
using System;
using Microsoft.Xna.Framework.Graphics;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.IO;

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
        private int currentItem = 1;
        private int percentage = 0;

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
            projDirectory += "\\Rigging and Animation";
        }

        public override void Update(GameTime gameTime)
        {

        }

        public override void DrawUI()
        {
            ImGui.Begin("Modemation");

            ImGui.Image(texPointer, new System.Numerics.Vector2(tex.Width, tex.Height));

            //Import input image
            if (ImGui.Button("Import Image"))
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
                    else if (result == DialogResult.Cancel)
                    {
                        System.Environment.Exit(0);
                    }
                }
            }

            //Import input video
            if (ImGui.Button("Import Video"))
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
                    else if (result == DialogResult.Cancel)
                    {
                        System.Environment.Exit(0);
                    }
                }
            }

            ImGui.Combo("Sampling Rate", ref currentItem, Enum.GetNames(typeof(SampleRate)), Enum.GetNames(typeof(SampleRate)).Length);

            if (ImGui.Button("Start"))
            {
                if (Directory.Exists(projDirectory + "\\inputs\\video") &&
                    Directory.Exists(projDirectory + "\\inputs\\image") &&
                    Directory.GetFiles(projDirectory + "\\inputs\\video").Length != 0 &&
                    Directory.GetFiles(projDirectory + "\\inputs\\image").Length != 0)
                {
                    frameSamplingRate = (int)(Enum.GetValues(typeof(SampleRate)).GetValue(currentItem));

                    Threader.Invoke(StartOperation, 0);
                }
            }

            ImGui.Text("Progress: " + percentage.ToString() + "%");

            ImGui.End();
        }

        void StartOperation()
        {
            string[] imagePreprocessing = new string[]
            {
                "cd " + projDirectory, //Go to the existing directory
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

            Utility.ExecuteCommand(imagePreprocessing, projDirectory);

            percentage = 5;

            //////////////////////////////////////////
        }
    }
}

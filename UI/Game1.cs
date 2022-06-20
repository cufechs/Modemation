using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;
using FN_Engine;

namespace GP
{
    /// <summary>
    /// This is the main type for your game.
    /// </summary>
    public class Game1 : Game
    {
        GraphicsDeviceManager graphics;
        SpriteBatch spriteBatch;
        Camera2D Camera;
        ////////<Variables>/////
        public static SpriteFont spriteFont;
        ////////////////////////

        public Game1()
        {
            graphics = new GraphicsDeviceManager(this);
            Content.RootDirectory = "Content";
            IsMouseVisible = true;
            Window.AllowUserResizing = false;
        }
    
        /// <summary>
        /// Allows the game to perform any initialization it needs to before starting to run.
        /// This is where it can query for any required services and load any non-graphic
        /// related content.  Calling base.Initialize will enumerate through any components
        /// and initialize them as well.
        /// </summary>
        protected override void Initialize()
        {
            // TODO: Add your initialization logic here
            //graphics.GraphicsProfile = GraphicsProfile.HiDef; //Uncomment this if you want more graphical capabilities
            graphics.SynchronizeWithVerticalRetrace = true;
            graphics.PreferMultiSampling = true;
            GraphicsDevice.PresentationParameters.MultiSampleCount = 8;
            graphics.ApplyChanges();
    
            base.Initialize();
        }
    
        private void ImportantIntialization()
        {
            // Create a new SpriteBatch, which can be used to draw textures.
            spriteBatch = new SpriteBatch(GraphicsDevice);
    
            /////////Camera And Resolution Independent Renderer/////// -> Mandatory
            Camera = new Camera2D();
            Camera.Zoom = 1f;
            Setup.Initialize(graphics, Content, spriteBatch, Window, Camera, this);
    
            ResolutionIndependentRenderer.Init(ref graphics);
            ResolutionIndependentRenderer.SetResolution(graphics.PreferredBackBufferWidth, graphics.PreferredBackBufferHeight, false);
            ResolutionIndependentRenderer.SetVirtualResolution(graphics.PreferredBackBufferWidth, graphics.PreferredBackBufferHeight);
    
            Window.ClientSizeChanged += SceneManager.ScreenSizeChanged;        }
    
        /// <summary>
        /// LoadContent will be called once per game and is the place to load
        /// all of your content.
        /// </summary>
        protected override void LoadContent()
        {
            ImportantIntialization();
            spriteFont = Content.Load<SpriteFont>("Font");
            // This bit of code handles the directories from a PC to another
            string WorkingDirectory = "";
            foreach (string S in Environment.CurrentDirectory.Split('\\'))
            {
                if (S == "bin")
                {
                    WorkingDirectory = WorkingDirectory.Remove(WorkingDirectory.Length - 1, 1);
                    break;
                }
    
                WorkingDirectory += S + '\\';
            }
    
            Environment.CurrentDirectory = WorkingDirectory + "\\Content";
            Setup.SourceFilePath = Environment.CurrentDirectory;
            Setup.IntermediateFilePath = Setup.SourceFilePath + "\\obj\\DesktopGL\\";
            Setup.OutputFilePath = WorkingDirectory + "\\bin\\Debug\\netcoreapp3.1\\Content";
            Setup.ConfigurePipelineMG();
    
            SceneManager.LoadScene_Serialization("Scenes\\DefaultScene");
    
            ResolutionIndependentRenderer.SetResolution(graphics.PreferredBackBufferWidth, graphics.PreferredBackBufferHeight, false);
            ResolutionIndependentRenderer.SetVirtualResolution(graphics.PreferredBackBufferWidth, graphics.PreferredBackBufferHeight);
        }
    
        /// <summary>
        /// Allows the game to run logic such as updating the world,
        /// checking for collisions, gathering input, and playing audio.
        /// </summary>
        /// <param name="gameTime">Provides a snapshot of timing values.</param>
        protected override void Update(GameTime gameTime)
        {
            Input.GetState(); //This has to be called at the start of update method!!
    
            if (GamePad.GetState(PlayerIndex.One).Buttons.Back == ButtonState.Pressed || Keyboard.GetState().IsKeyDown(Keys.Escape))
                Exit();
    
            SceneManager.Update(gameTime);
    
            base.Update(gameTime);
        }
    
        /// <summary>
        /// This is called when the game should draw itself.
        /// </summary>
        /// <param name="gameTime">Provides a snapshot of timing values.</param>
        protected override void Draw(GameTime gameTime)
        {
            SceneManager.Draw(gameTime);
    
            base.Draw(gameTime);
        }
    }
}
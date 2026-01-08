{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-23.11"; # Or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.nodejs_20
    (pkgs.python311.withPackages (ps: [
      ps.flask
    ]))
  ];
  # Sets environment variables in the workspace
  env = {};
  # Search for the extensions you want on https://open-vsx.org/ and add them here
  extensions = [
    "ms-python.python"
    "ms-python.debugpy"
  ];

  # Enable previews
  previews = {
    enable = true;
    previews = {
      # Frontend (React App)
      web = {
        command = ["npm" "run" "dev" "--" "--port" "$PORT"];
        manager = "web";
        cwd = "frontend"; # Run in the frontend directory
      };
      # Backend (Flask API)
      api = {
        command = ["python" "-m" "flask" "run" "--host=0.0.0.0" "--port=5000"];
        manager = "process";
        env = {
            FLASK_APP = "app.py";
        };
      };
    };
  };

  # Workspace lifecycle hooks
  workspace = {
    # Runs when a workspace is first created
    onCreate = {
      "install-dependencies" = "npm install --prefix frontend && pip install -r requirements.txt";
    };
    # Runs when the workspace is (re)started
    onStart = {
      # The preview commands now handle starting the servers
    };
  };
}

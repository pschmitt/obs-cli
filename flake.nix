{
  description = "Flake for obs-cli development and packaging";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
        pyPkgs = python.pkgs;

        obswsPython = pyPkgs.buildPythonPackage rec {
          pname = "obsws-python";
          version = "1.6.2";
          pyproject = true;

          src = pyPkgs.fetchPypi {
            pname = "obsws_python";
            inherit version;
            hash = "sha256-cR1gnZ5FxZ76SD9GlHSIhv142ejsqs/Bp8wV1A1kfdw=";
          };

          nativeBuildInputs = [
            pyPkgs.hatchling
          ];

          propagatedBuildInputs = [
            pyPkgs.tomli
            pyPkgs.websocket-client
          ];

          doCheck = false;

          meta = with pkgs.lib; {
            description = "Python SDK for OBS Studio WebSocket v5.0";
            homepage = "https://github.com/aatikturk/obsws-python";
            license = licenses.gpl3;
            maintainers = with maintainers; [ pschmitt ];
          };
        };

        obsCli = pyPkgs.buildPythonApplication {
          pname = "obs-cli";
          version = "0.8.3";
          src = ./.;
          pyproject = true;
          nativeBuildInputs = with pyPkgs; [
            setuptools
            setuptools-scm
            wheel
          ];
          propagatedBuildInputs = with pyPkgs; [
            obswsPython
            rich
          ];
          pythonImportsCheck = [ "obs_cli" ];
          meta = with pkgs.lib; {
            description = "CLI for controlling OBS Studio";
            homepage = "https://github.com/pschmitt/obs-cli";
            license = licenses.gpl3Only;
            maintainers = with maintainers; [ pschmitt ];
            mainProgram = "obs-cli";
          };
        };

        devTools = python.withPackages (
          ps: with ps; [
            black
            ipython
            neovim
            ruff
          ]
        );
      in
      {
        packages = {
          default = obsCli;
          obs-cli = obsCli;
          obsws-python = obswsPython;
        };

        devShells.default = pkgs.mkShell {
          name = "obs-cli-devshell";
          packages = [
            devTools
            pkgs.git
            pkgs.pre-commit
            pkgs.uv
          ];
          shellHook = ''
            export PYTHONPATH="''${PWD}:''${PYTHONPATH:-}"
            export UV_PROJECT_ENVIRONMENT=".venv"
            echo "Entering obs-cli dev shell (Python ${python.version})."
            echo "Run 'uv sync' to populate .venv and 'obs-cli --help' to get started."
          '';
        };
      }
    );
}

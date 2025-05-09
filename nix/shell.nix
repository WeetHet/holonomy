{ pyproject-nix, pkgs, ... }:
let
  python = pkgs.python3;
  project = pyproject-nix.lib.project.loadPyproject { projectRoot = ../.; };
  pythonEnv = project.renderers.withPackages {
    inherit python;
    groups = [ "dev" ];
  };
  pythonDrv = python.withPackages pythonEnv;
  pythonToLink = pkgs.symlinkJoin {
    name = "python-holonomy-env";
    paths = [
      pythonDrv
      pkgs.ruff
      pkgs.pyright
    ];
  };
  relaxedDeps.pythonRelaxDeps = [ "plotly" ];
  holonomy = python.pkgs.buildPythonPackage (
    relaxedDeps
    // project.renderers.buildPythonPackage {
      inherit python;
      groups = [ "dev" ];
    }
  );
in
{
  devShells.default = pkgs.mkShell {
    packages = [
      pkgs.uv

      holonomy

      pythonDrv
      pkgs.ruff
      pkgs.pyright

      pkgs.npins
      pkgs.koji
    ];

    shellHook = ''
      ln -snf ${pythonToLink} .python-env
      [[ -d .venv ]] && source .venv/bin/activate
    '';

    env.UV_NO_SYNC = 1;
  };
}

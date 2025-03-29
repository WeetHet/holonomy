{
  system ? builtins.currentSystem,
  sources ? import ./npins,
  pkgs ? import sources.nixpkgs { inherit system; },
  pyproject-nix ? import sources.pyproject-nix { inherit lib; },
  lib ? pkgs.lib,
}:
let
  project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
  python = pkgs.python3;
  pythonEnv = project.renderers.withPackages { inherit python; };
in
pkgs.mkShell {
  packages = [
    pkgs.uv

    (python.withPackages pythonEnv)
    pkgs.ruff
    pkgs.pyright

    pkgs.npins
  ];

  shellHook = ''
    [[ -d .venv ]] && source .venv/bin/activate
  '';
}

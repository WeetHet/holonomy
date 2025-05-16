{ self, inputs, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      python = pkgs.python3;
      project = inputs.pyproject-nix.lib.project.loadPyproject { projectRoot = ../.; };
      pythonEnv = project.renderers.withPackages {
        inherit python;
        groups = [ "dev" ];
      };
      pythonDrv = python.withPackages pythonEnv;
      env = {
        nativeBuildInputs = [
          pkgs.pyright
          pythonDrv
        ];
      };
    in
    {
      checks.pyright = pkgs.runCommand "pyright-check" env ''
        pushd ${self} && pyright holonomy && popd
        touch $out
      '';
    };
}

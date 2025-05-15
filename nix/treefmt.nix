{ ... }:
{
  treefmt = {
    projectRootFile = "flake.nix";
    programs.ruff = {
      check = true;
      format = true;
    };
    programs.nixfmt.enable = true;
    programs.shfmt.enable = true;
    programs.taplo.enable = true;

    settings = {
      excludes = [
        "*.md"
        "nix"
        "*.png"
      ];
      formatter.ruff-check.priority = 1;
      formatter.ruff-format.priority = 2;
    };
  };
}

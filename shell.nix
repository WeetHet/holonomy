{
  system ? builtins.currentSystem,
  sources ? import ./npins,
  pkgs ? import sources.nixpkgs { inherit system; },
}:
pkgs.mkShell {
  packages = [
    pkgs.uv
    pkgs.python3
    pkgs.npins
  ];
}

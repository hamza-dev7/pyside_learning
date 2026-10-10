{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    (pkgs.python314.withPackages (ps: [
        ps.pyside6
    ]))
  ];
}

#!/usr/bin/env python

from distutils.core import setup

install_requires = (
    'supriya',
    )


def main():
    setup(
        author='Josiah Wolf Oberholtzer',
        author_email='josiah.oberholtzer@gmail.com',
        install_requires=install_requires,
        name='pipermeth001',
        packages=('pipermeth001',),
        url='https://github.com/josiah-wolf-oberholtzer/pipermeth001',
        version='0.1',
        zip_safe=False,
        )


if __name__ == '__main__':
    main()

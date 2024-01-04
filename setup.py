from setuptools import setup, find_namespace_packages

install_requires = []
requirements_txt = "PyHooking/requirements.txt"
with open(requirements_txt) as f: install_requires = f.read().split("\n")
install_requires = list(filter(lambda e: len(e) > 0, install_requires))

setup(
    name="PyHooking",
    version="1.0",
    author="Vic P.",
    author_email="vic4key@gmail.com",
    packages=find_namespace_packages(exclude=["Examples", "build", "dist"]),
    url="https://github.com/vic4key/py-hooking.git",
    license="LICENSE",
    description="PyHooking for Python",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=install_requires,
    include_package_data=True,
    package_data={},
)
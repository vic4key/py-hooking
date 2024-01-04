BITS := $(shell python -c "import struct;print(struct.calcsize('P') * 8)")
ARCH := $(shell python -c "import platform;print(platform.machine().lower())")

NAME   := mylib
SOURCE := $(NAME).cpp
OUTPUT := $(NAME)_$(ARCH)_$(BITS)

ifeq ($(ARCH), amd64)           # Windows
  CXX = cl
  EXT = dll
  OBJ = *.obj *.exp *.lib
	ARG = /LD /MT /Fe:$(OUTPUT).$(EXT)
else ifeq ($(ARCH), x86_64)     # Linux
  CXX = g++
  EXT = so
	ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(ARCH), aarch64)    # Android
  CXX = g++
  EXT = so
	ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(ARCH), Darwin)     # iOS, MacOS
  CXX = clang
  EXT = dylib
	ARG = -shared -o $(OUTPUT).$(EXT)
else
  $(error unsupported platform)
endif

$(OUTPUT).$(EXT): $(SOURCE)
	$(CXX) $(ARG) $(SOURCE)

.PHONY: clean
clean:
  ifneq ($(OBJ),)
	  @rm -f $(OBJ)
  endif

.PHONY: clean-all
clean-all:
	@rm -f $(OBJ) $(OUTPUT).$(EXT)
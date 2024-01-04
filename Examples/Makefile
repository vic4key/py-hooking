# OS Mode

BITS := $(shell python -c "import struct;print(struct.calcsize('P') * 8)")      # [32, 64]
BITS := $(strip $(BITS))

# OS Arch

ARCH := $(shell python -c "import platform;print(platform.machine().lower())")  # [x86_64, aarch64]
ARCH := $(strip $(ARCH))

ifeq ($(ARCH),amd64)
  ARCH := x86_64
endif

ifneq ($(findstring iphone,$(ARCH)),)
  ARCH := aarch64
endif

# OS Type

TYPE := $(shell python -c "import platform;print(platform.system().lower())")   # [windows, linux, android, macos, ios]
TYPE := $(strip $(TYPE))

ifeq ($(TYPE),linux)
  ifeq ($(ARCH),aarch64) 
    TYPE := android
  endif
endif

ifeq ($(TYPE),darwin)
  ifeq ($(ARCH),x86_64) 
    TYPE := macos
  else
    TYPE := ios
  endif
endif

$(info OS Type = '$(TYPE)'; OS Arch = '$(ARCH)'; OS Bits = '$(BITS)')

NAME   := mylib
SOURCE := $(NAME).cpp
OUTPUT := $(NAME)_$(ARCH)_$(BITS)

ifeq ($(TYPE),windows)        # Windows
  CXX = cl
  EXT = dll
  OBJ = *.obj *.exp *.lib
  ARG = /LD /MT /Fe:$(OUTPUT).$(EXT)
else ifeq ($(TYPE),linux)     # Linux
  CXX = g++
  EXT = so
  ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(TYPE),android)   # Android
  CXX = g++
  EXT = so
  ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(TYPE),macos)     # MacOS
  CXX = clang
  EXT = dylib
  ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(TYPE),ios)       # iOS
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

# OS Mode

OS_BITS := $(shell python3 -c "import struct;print(struct.calcsize('P') * 8)")      # [32, 64]
OS_BITS := $(strip $(OS_BITS))

# OS Arch

OS_ARCH := $(shell python3 -c "import platform;print(platform.machine().lower())")  # [i686, x86_64, aarch64]
OS_ARCH := $(strip $(OS_ARCH))

ifeq ($(OS_ARCH),amd64)
  OS_ARCH := x86_64
endif

ifneq ($(findstring iphone,$(OS_ARCH)),)
  OS_ARCH := aarch64
endif

# OS Type

OS_TYPE := $(shell python3 -c "import platform;print(platform.system().lower())")   # [windows, linux, macos, ios, android]
OS_TYPE := $(strip $(OS_TYPE))

ifeq ($(OS_TYPE),linux)
  ifeq ($(OS_ARCH),aarch64) 
    OS_TYPE := android
  endif
endif

ifeq ($(OS_TYPE),darwin)
  ifeq ($(OS_ARCH),x86_64) 
    OS_TYPE := macos
  else
    OS_TYPE := ios
  endif
endif

# OS Name

OS_NAME = $(OS_TYPE)

ifeq ($(OS_NAME),linux)
  ifeq ($(OS_ARCH),aarch64)
    OS_NAME := android
  endif
endif

ifeq ($(OS_NAME),darwin)
  ifeq ($(OS_ARCH),aarch64)
    OS_NAME := ios
  else
    OS_NAME := macos
  endif
endif

# $(info OS Type = '$(OS_TYPE)'; OS Bits = '$(OS_BITS)'; OS Name = '$(OS_NAME)'; OS Arch = '$(OS_ARCH)')
$(info Compiling with `$(OS_TYPE)-$(OS_BITS):$(OS_NAME)-$(OS_ARCH)`)

NAME   := mylib
SOURCE := $(NAME).cpp
OUTPUT := $(NAME)_$(OS_ARCH)_$(OS_BITS)

ifeq ($(OS_TYPE),windows)        # Windows
  CXX = cl
  EXT = dll
  OBJ = *.obj *.exp *.lib
  ARG = /LD /MT /Fe:$(OUTPUT).$(EXT)
else ifeq ($(OS_TYPE),linux)     # Linux
  CXX = g++
  EXT = so
  ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(OS_TYPE),android)   # Android
  CXX = g++
  EXT = so
  ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(OS_TYPE),macos)     # MacOS
  CXX = clang
  EXT = dylib
  ARG = -shared -o $(OUTPUT).$(EXT)
else ifeq ($(OS_TYPE),ios)       # iOS
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

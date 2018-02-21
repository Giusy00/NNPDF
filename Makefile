#############################################
# Makefile to generate BUILDMASTER Program
# make => for main version
# make clean   => to clean project
#############################################

# Macros for results folders
RESULTDIR = results
RESULTSDIR= -D  RESULTS_PATH="results"
DATADIR=    -D  DATA_PATH="./"
MACROS = $(RESULTSDIR) $(DATADIR)

# Compiler options
##################

# NNPDF flags
NNPDFCXX = $(shell pkg-config nnpdf --cflags)
NNPDFLD  = $(shell pkg-config nnpdf --libs)

# YAML-cpp flags
YAMLLD  = $(shell pkg-config yaml-cpp --libs)
YAMLCXX = $(shell pkg-config yaml-cpp --cflags)

# GSL flags
GSLCXX = $(shell gsl-config --cflags)
GSLLD  = $(shell gsl-config --libs)

CXXFLAGS=-Wall -g -I ./inc -I ./src  -std=c++14 $(NNPDFCXX) $(GSLCXX) $(MACROS) $(YAMLCXX)
LDFLAGS= $(NNPDFLD) $(GSLLD) $(YAMLLD)

#####################################

all: buildmaster

.PHONY: clean
clean:
	rm -rf buildmaster
	rm -rf ./src/*.o
	rm -rf ./filters/*.o
	rm -rf $(RESULTDIR)/*

######### Programs BUILDMASTER #########
########################################

buildmaster_src = src/buildmaster.o \
                  src/buildmaster_utils.o \
	   	  		  src/common.o 

filter_src = $(wildcard filters/*.cc)
filter_obj = $(filter_src:.cc=.o)

buildmaster_src += $(filter_obj)

buildmaster: $(buildmaster_src)
	$(CXX) $(CFLAGS) $(buildmaster_src) -o buildmaster $(LDFLAGS)

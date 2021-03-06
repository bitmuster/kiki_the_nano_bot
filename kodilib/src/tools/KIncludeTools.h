/*
 *  KIncludeTools.h
 *  kodisein
 */

#ifndef __KIncludeTools
#define __KIncludeTools

#ifdef WIN32
#pragma warning ( disable : 4800 4305 4267 ) // Disable warnings
#endif

#ifdef K_INCLUDE_GLUT
#	if defined(__APPLE__) && defined(__MACH__) || defined(_WIN32)
#		include <GLUT/glut.h>
#	else
#		include <GL/glut.h>
#	endif
#endif

#ifdef K_INCLUDE_GLU
#	if defined(__APPLE__) && defined(__MACH__)
#		include <OpenGL/glu.h>
#	else
#		include <GL/glu.h>
#	endif
#endif

#endif


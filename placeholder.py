#!/usr/bin/env python
# encoding: utf-8;

from __future__ import with_statement

import os, sys, re, numpy
from optparse import OptionParser, OptionValueError

try:
    from png import Writer
except ImportError:
    from lib.png import Writer

characters = {
    '0':    [   [ 0, 1, 1, 0, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ] ],

    '1':    [   [ 0, 1, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 1, 1, 1, 0 ] ],

    '2':    [   [ 1, 1, 1, 0, 0 ],
                [ 0, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ],
                [ 1, 0, 0, 0, 0 ],
                [ 1, 1, 1, 1, 0 ] ],

    '3':    [   [ 1, 1, 1, 0, 0 ],
                [ 0, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ],
                [ 0, 0, 0, 1, 0 ],
                [ 1, 1, 1, 0, 0 ] ],

    '4':    [   [ 1, 0, 1, 0, 0 ],
                [ 1, 0, 1, 0, 0 ],
                [ 1, 1, 1, 1, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ] ],

    '5':    [   [ 1, 1, 1, 1, 0 ],
                [ 1, 0, 0, 0, 0 ],
                [ 1, 1, 1, 0, 0 ],
                [ 0, 0, 0, 1, 0 ],
                [ 1, 1, 1, 0, 0 ] ],

    '6':    [   [ 0, 1, 1, 0, 0 ],
                [ 1, 0, 0, 0, 0 ],
                [ 1, 1, 1, 0, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ] ],

    '7':    [   [ 1, 1, 1, 1, 0 ],
                [ 0, 0, 0, 1, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 1, 0, 0, 0 ],
                [ 0, 1, 0, 0, 0 ] ],

    '8':    [   [ 0, 1, 1, 0, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ] ],

    '9':    [   [ 0, 1, 1, 0, 0 ],
                [ 1, 0, 0, 1, 0 ],
                [ 0, 1, 1, 1, 0 ],
                [ 0, 0, 0, 1, 0 ],
                [ 0, 1, 1, 0, 0 ] ],

    '(':    [   [ 0, 0, 0, 1, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 0, 1, 0 ] ],

    ')':    [   [ 0, 1, 0, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 1, 0, 0, 0 ] ],

    'x':    [   [ 0, 0, 0, 0, 0 ],
                [ 0, 1, 0, 1, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 1, 0, 1, 0 ],
                [ 0, 0, 0, 0, 0 ] ],

    ':':    [   [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 1, 0, 0 ],
                [ 0, 0, 0, 0, 0 ] ],

    '~':    [   [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 0, 0, 0 ],
                [ 0, 1, 0, 1, 0 ],
                [ 1, 0, 1, 0, 0 ],
                [ 0, 0, 0, 0, 0 ] ],

    ' ':    [   [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 0, 0, 0 ],
                [ 0, 0, 0, 0, 0 ] ]
}

class PlaceholderOptionError( Exception ):
    pass

class Placeholder( object ):
    FOREGROUND = 255
    BACKGROUND = 0
    def __init__( self, width=100, height=100, background="DDDDDD", foreground="333333", out="png.png", border=True, metadata=True ):
        self.width      = width
        self.height     = height
        self.out        = out
        self.border     = border
        self.metadata   = metadata
        self.colors     = self.generateColors( background, foreground )

    def generateColors( self, start, end ):
        colors  = []
        steps   = Placeholder.FOREGROUND * 1.0
        
        try:
            start   = ( int( start[0:2], 16 ),  int( start[2:4], 16 ),  int( start[4:6], 16 ) )
            end     = ( int( end[0:2], 16 ),    int( end[2:4], 16 ),    int( end[4:6], 16 ) )
        except ValueError as ex:
            raise PlaceholderOptionError( 'Please enter something resembling an actual hex value: "%s"' % str( ex ) )

        step    = ( (end[0]-start[0])/steps, (end[1]-start[1])/steps, (end[2]-start[2])/steps )
        for rgb in range( 0, int( steps ) ):
            colors.append( (
                int( step[0]*rgb + start[0]),
                int( step[1]*rgb + start[1]),
                int( step[2]*rgb + start[2])))
        return colors

    def getColor( self, opacity ):
        return int( 255 * opacity )

    def calculateAspectRatio( self ):
        def gcd(a, b):
            if b == 0:
                return a
            return gcd(b, a % b)
        def lcm(a, b):
            return a * b / gcd( a, b )

        #
        #   Fake some common ratios with a margin of error
        #
        actualRatio = ( 1.0 * self.width ) / self.height

        if ( abs( 1 - actualRatio ) < 0.02 ):
            return "~1:1"
        elif ( abs( 16 / 9 - actualRatio ) < 0.02 ):
            return "~16:9"
        elif ( abs( 9 / 16 - actualRatio ) < 0.02 ):
            return "~9:16"
        elif ( abs( 4 / 3 - actualRatio ) < 0.02 ):
            return "~4:3"
        elif ( abs( 3 / 4 - actualRatio ) < 0.02 ):
            return "~3:4"
        else:
            w = lcm( self.width, self.height ) / self.height
            h = lcm( self.width, self.height ) / self.width
            return "%d:%d" % ( w, h )

    def addMetadata( self, pixels ):
        shortMetadataString = "%dx%d" % ( self.width, self.height )
        metadataString      = "%s (%s)" % ( shortMetadataString, self.calculateAspectRatio() )
        if ( len( metadataString ) * 5 > self.width - 7 ):
            if ( len( shortMetadataString ) * 8 <= self.width - 7 ):
                metadataString = shortMetadataString
            else:
                metadataString = None

        if metadataString is not None:
            startX = self.width  - len( metadataString ) * 5 - 7;
            startY = self.height - 8 - 2;
            color  = 1
            for x in range( startX, self.width - 2 ):
                for y in range( startY, self.height - 2 + 1 ):
                    if x >= startX + 4 and x < self.width - 4 + 1 and y >= startY + 2 and y < startY + 5 + 2:
                        char  = int( ( x - ( startX + 4 ) ) / 5 )
                        charX = ( x - ( startX + 4 ) ) % 5
                        charY = ( y - ( startY + 2 ) ) % 5
                        if charX == 0 and charY == 0:
                            color = 0 if color == 1 else 1
                        pixels[ y, x ] = Placeholder.BACKGROUND if ( characters[ metadataString[ char ] ][ charY ][ charX ] == 1 ) else Placeholder.FOREGROUND
                    else:
                        pixels[ y, x ] = Placeholder.FOREGROUND

    def write( self ):
        slope       = ( 1.0 * self.height ) / self.width
        pixels      = numpy.zeros( ( self.height, self.width ), dtype=int )

        #
        # Something similar to http://en.wikipedia.org/wiki/Xiaolin_Wu's_line_algorithm
        # but special cased, since I know the lines are mirrored thrice.
        #
        actualY = 0
        for leftX in range( 0, ( self.width / 2 ) + 1 ):
            # Precalculating.  Math!
            frac        = actualY - int( actualY ) 
            topColor    = self.getColor( 1 - frac )
            bottomColor = self.getColor( frac )
            topY        = int( actualY )
            bottomY     = self.height - topY - 1
            rightX      = self.width - leftX - 1

            # Actual Line (top-left)
            pixels[ topY,       leftX ]   = topColor
            pixels[ topY + 1,   leftX ]   = bottomColor

            # Horizontal Flip (top-right)
            pixels[ topY,       rightX ]  = topColor
            pixels[ topY + 1,   rightX ]  = bottomColor

            # Vertical Flip (bottom-left)
            pixels[ bottomY,     leftX ]  = topColor
            pixels[ bottomY - 1, leftX ]  = bottomColor

            # 180-degree Rotation
            pixels[ bottomY,     rightX ] = topColor
            pixels[ bottomY - 1, rightX ] = bottomColor
            
            # Increment `actualY`
            actualY += slope
            
            # Worry about the border (avoids another loop)
            if self.border:
                pixels[ 0,                leftX  ] = Placeholder.BACKGROUND
                pixels[ self.height - 1,  leftX  ] = Placeholder.BACKGROUND
                pixels[ 0,                rightX ] = Placeholder.BACKGROUND
                pixels[ self.height - 1,  rightX ] = Placeholder.BACKGROUND
                if leftX > 1:
                    pixels[ 1,                leftX  ] = Placeholder.FOREGROUND
                    pixels[ self.height - 2,  leftX  ] = Placeholder.FOREGROUND
                    pixels[ 1,                rightX ] = Placeholder.FOREGROUND
                    pixels[ self.height - 2,  rightX ] = Placeholder.FOREGROUND
                if leftX == 1:
                    for y in range( 1, self.height - 1 ):
                        pixels[ y,  leftX  ] = Placeholder.FOREGROUND
                        pixels[ y,  rightX ] = Placeholder.FOREGROUND

        if self.metadata: 
            self.addMetadata( pixels )

        with open( self.out, 'wb' ) as f:
            w = Writer( self.width, self.height, background=self.colors[0], palette=self.colors, bitdepth=8 )
            w.write( f, pixels )

def is_valid_hex( option, opt_str, value, parser ):
    try:
        r,g,b = ( int( value[0:2], 16 ),  int( value[2:4], 16 ),  int( value[4:6], 16 ) )
        if len(value) == 6 and min( r, g, b ) >= 0 and max( r, g, b ) <= 255:
            setattr(parser.values, option.dest, value )
            return
    except:
        pass
    raise OptionValueError(
            """
    `%s` expects a hex value in `RRGGBB` format (`000000` for black, and `FFFFFF` white).
    You entered `%s`""" % (opt_str, value))

def main(argv=None):
    if argv is None:
        argv = sys.argv

    default_root = os.path.dirname(os.path.abspath(__file__))

    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 0.1")
    parser.add_option(  "--verbose",
                        action="store_true", dest="verbose_mode", default=False,
                        help="Verbose mode")
    
    parser.add_option(  "-o", "--output",
                        action="store",
                        dest="out", 
                        default=os.path.join(default_root, 'png.png'),
                        help="Output file")

    parser.add_option(  "--background",
                        action="callback",
                        type="string",
                        dest="background",
                        default="000000",
                        metavar="RRGGBB",
                        callback=is_valid_hex,
                        help="Background color in hex (`RRGGBB`) format")

    parser.add_option(  "--foreground",
                        action="callback",
                        type="string",
                        dest="foreground",
                        default="FFFFFF",
                        metavar="RRGGBB",
                        callback=is_valid_hex,
                        help="Foreground color in hex (`RRGGBB`) format")

    parser.add_option(  "--width",
                        action="store",
                        dest="width",
                        type="int",
                        default=100,
                        help="Width of placeholder")

    parser.add_option(  "--height",
                        action="store",
                        dest="height",
                        type="int",
                        default=100,
                        help="Height of placeholder")
    
    parser.add_option(  "--no-border",
                        action="store_false",
                        dest="border",
                        type=None,
                        default=True,
                        help="Suppress rendering of border around the placeholder image.")

    parser.add_option(  "--no-metadata",
                        action="store_false",
                        dest="metadata",
                        type=None,
                        default=True,
                        help="Suppress rendering of the placeholder's image size/aspect ratio.")
    
    (options, args) = parser.parse_args()

    p = Placeholder(    width=options.width, height=options.height, background=options.background,
                        foreground=options.foreground, out=options.out, border=options.border,
                        metadata=options.metadata )
    p.write()

if __name__ == "__main__":
    sys.exit( main() )

import sys
from array import array

import pygame
import moderngl

pygame.init()

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)
ctx = moderngl.create_context()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
]))

scene_fbo = ctx.framebuffer(color_attachments=[ctx.texture((screen_width, screen_height), 4)])
bright_parts_fbo = ctx.framebuffer(color_attachments=[ctx.texture((screen_width, screen_height), 4)])

vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;

in vec2 uvs;
out vec4 f_color;

void main() {
    vec4 texColor = texture(tex, uvs);
    float brightness = dot(texColor.rgb, vec3(0.2126, 0.7152, 0.0722)); // Luminance calculation
    if (brightness > 0.7) { // Threshold for bright parts
        f_color = texColor; // Keep bright parts
    } else {
        f_color = vec4(0.0, 0.0, 0.0, 1.0); // Make non-bright parts black
    }
}
'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(pygame.image.tostring(surf, 'RGBA', True))
    return tex

clock = pygame.time.Clock()

img = pygame.image.load('../../assets/sprites/title.png')
img_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
img_surface.blit(img, (0, 0))  # Adjust position as needed

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    ctx.clear(0.0, 0.0, 0.0, 1.0)
    frame_tex = surf_to_texture(img_surface)
    frame_tex.use()
    program['tex'] = 0
    render_object.render(moderngl.TRIANGLE_STRIP)
    frame_tex.release()

    pygame.display.flip()
    clock.tick(60)

#version 330

uniform mat4 u_projectionMatrix;
uniform mat4 u_modelMatrix;

in vec2 in_vert;

void main() {
    gl_Position = u_projectionMatrix * u_modelMatrix * vec4(in_vert, 0.0, 1.0);
}

# plugins/filters/grain_filter.py

from .base_filter import BaseFilter
import bpy

class GrainFilter(BaseFilter):
    name = "grain_filter"

    def apply(self, seq, fps):
        """
        Adiciona granulado de filme simulando ruído de luminância sobre todo o frame.
        Implementamos no compositor:
        - VSE → Mix (com imagem de ruído procedimental) → Composite.
        """
        scene = bpy.context.scene
        scene.use_nodes = True
        scene.render.use_sequencer = True
        tree = scene.node_tree
        links = tree.links

        # Limpa nós existentes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Entrada VSE
        vseq_node = tree.nodes.new(type="CompositorNodeRLayers")
        vseq_node.location = (-300, 300)
        vseq_node.label = "VSE Input"

        # Cria Noise Texture (procedural) → preciso usar Texture Node
        noise_node = tree.nodes.new(type="CompositorNodeTexMusgrave")
        noise_node.location = (-300, 0)
        scale = self.params.get("scale", 10.0)
        noise_node.inputs["Scale"].default_value = scale

        # Cria Mix Node para combinar VSE + Noise
        mix_node = tree.nodes.new(type="CompositorNodeMixRGB")
        mix_node.blend_type = 'ADD'
        mix_node.location = (0, 150)
        noise_intensity = self.params.get("intensity", 0.1)
        mix_node.inputs[0].default_value = noise_intensity  # influência do ruído

        # Saída Composite
        comp_node = tree.nodes.new(type="CompositorNodeComposite")
        comp_node.location = (300, 150)

        # Conexões
        links.new(vseq_node.outputs[0], mix_node.inputs[1])
        links.new(noise_node.outputs[0], mix_node.inputs[2])
        links.new(mix_node.outputs[0], comp_node.inputs[0])

# mdl-exporter
Warcraft MDL exporter for Blender
By Kalle Halvarsson

## Installation
* Add mdl-exporter folder to a zip or rar file
* In Blender, go to User Preferences (CTRL+ALT+U) and select "Install Add-on From File". Select your zipped folder.
* The option to export to .mdl will now appear in the export menu (you may need to restart Blender first).

## Instructions
This plugin tries to approximate the functionality of the Wc3 Art Tools exporter for 3ds Max. The ambition has been to support multiple ways of achieving the same result, so that users can set up their scene in whatever way feels most intuitive. There are, however, some implementation details you might need to know before using this plugin.

### Materials
This exporter comes with a custom material editor which will attach extra MDL properties to the materials in your file. A material consists of multiple material layers, which will be rendered from top to bottom, and blended together using the specified filter mode. Some filter modes support an additional alpha multiplier, which can be animated. To add a texture animation, create a mapping node in the node graph with the same name as your layer, and animate its properties (will be implemented soon).  

![Material Editor](https://github.com/khalv/mdl-exporter/blob/master/images/Material%20Editor.jpg)

If no data is specified, the exporter will attempt to derive the material's properties from whatever data exists. This is a legacy feature and there is really no reason for doing this other than if you already have a node setup and want to attempt at exporting a similar look. 

#### Cycles Materials (Nodes)
If the material is a Cycles Node Graph, the fallback solution is to traverse the node tree looking for texture nodes. Each Mix node near the output will split the layer into two. Using an Emissive BSDF will cause the layer to become unshaded. Feeding a mapping node into the UV slot of a texture node and animating its properties will create a texture animaiton. 

#### BI Materials
Blender Internal materials are based on textures being layered on top of each other using different blend modes, similar to how WC3 materials work. The fallback exporter for these will use each texture slot as a layer, and use the blend mode as filter mode. Adding an emissive factor will make the layer unshaded, and adding or animating an alpha factor will control the Alpha property of the layer (for Blend, Additive Alpha, and Transparent filter modes). 

### Geosets
MDL files split up meshes into "geosets" based on material, where each geoset corresponds to geometry sharing the same material. As such, assigning multiple materials onto the same object will cause it to be split into as many geosets. Each geoset must be associated with at least one bone - if the mesh is not parented to a bone, one will be created for it. It is possible to skin an armature to a mesh - however, having vertices not assigned to a bone group may cause issues. Any object which isn't a mesh and whose name starts with "Bone_" can be treated as a bone. 

### Animations
It is possible to animate the position, scale and rotation of bones or meshes, but support for axis correciton is currently experimental and might screw up the rotations. You can also animate an object's visibility by keyframing the "render visibility" property (you can do this by holding your mouse over the render icon in the outliner and pressing the I key) - optionally, you can create a custom property called "visibility" and animate that. Using the Color field of an object, you can animate its tint value. Linear, DontInterp, and Bezier interpolation modes are currently supported for scaling and translation, Wc3 rotations use Hermite instead of Bezier interpolation - this is currently has some approximate and temporary support which might not produce exactly the same result as you'd get from Wc3 Art Tools. Quaternion interpolation is very abstract and i'll fix this one i've wrapped my head around it. 

#### Sequences
To mark sequences, create timeline markers (using the M key while hovering over the timeline) and rename them (using CTRL+M) to the name of your animation. Each sequence requires both a start and an end key with the same name. This approach was chosen over using acitons because it was deemed to be more intuitive and similar to how the process works in Wc3 Art Tools. If no sequence exists, a default one will be added.

#### Global Sequences
Adding a "Cycles" modifier to an f-curve will create a global sequence around it. Global sequences always start from frame 0. Only the first channel (X for scale/rotation/translation, R for RGB color) is checked for a modifier. 

### Attachment Points
To create an attachment point, simply create an empty object and give it a name which ends with the word "Ref". For example, "Overhead Ref" will produce an attachment point called "Overhead". 

### Event Objects
Similar to attachments, event objects are created by giving an empty object a name which starts with an event type ("UBR" for UberSplat, "SND" for Sound, "FTP" for FootPrint, "SPL" for BloodSplat). The type is followed by a number ID (can be 'x'), and ends with the event identifier. An example of an event object is "SND1DHLB", which would produce a "Human Building Death (large)" sound. To animate the event, create a custom property called "eventtrack" and animate its value - the positions of the keyframes are used to trigger the event.

There is a helper operator for creating event objects which you can find by pressing the spacebar and searching for "Add MDL event track". These will give you fields where you can select the exact type and ID name from a list of names.

### Collision Shapes
Collision shapes in Warcraft are used primarily to define the selectable area of a unit. You can create theese by adding any geometric shape and naming it "CollisionBox" or "CollisionSphere". The exporter will use the bounds to calculate a radius or min/max points automatically. Note that collision boxes are always saved as axis aligned. There will be helper operators for quickly creating collision shapes named "Add MDL Collison Box" and "Add MDL Collision Sphere" respectively.  

### Cameras
Cameras are exported as-is.

### Lights
Switch to Blender Render to get more alternatives for changing the properties of your lights. Lights which are not Point or Directional will be considered Ambient. Attenuation always starts at 0 and ends with the max range of the light. Future versions will support animating range and energy values. A custom light editor is on the roadmap. 

### Particle Systems
The exporter has a custom editor for configuring particle systems. The data piggybacks on the Blender ParticleSystemSettings data block, so you need to create a particle system to make the MDL particle editor appear. This also allows for shared particle data among emitters - just remember to make it single-user first if you copy one so that you don't overwrite your old data. I've chosen to name the emitters "Model Emitter", and "Particle Emitter" rather than "ParticleEmitter" and "ParticleEmitter2", since it's more descriptive of what they do. Ribbons are also supported. The bounds of whatever object the particle system is attached to defines the width and height of the emitter. 



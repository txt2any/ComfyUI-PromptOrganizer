import { app } from "../../../scripts/app.js";

app.registerExtension({
	name: "Comfy.Txt2Any.PromptOrganizer",
	async init(app) {},
	async setup(app) {},
  async addCustomNodeDefs(defs, app) {},
  async getCustomWidgets(app) {},
	async beforeRegisterNodeDef(nodeType, nodeData, app) {},
  async registerCustomNodes(app) {},
  loadedGraphNode(node, app) {
    if (node.type == 'SaveImageToT2A') {
      const url = 'https://www.txt2any.com'
      function openInT2a(filename) {
        try {
          window.open(url + '/#/cloud?filename=' + filename)
        } catch(e) {
          window.open(url + '/#/cloud')
        }
      }
      node.addWidget("button","View in txt2any", null, function(v){
        if (node.images) {
          node.images.forEach( image => {
            openInT2a(image.filename)
          });
        }
      }, {} );
    }
  },
	nodeCreated(node, app) {},
})
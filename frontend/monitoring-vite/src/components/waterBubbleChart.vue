<template>
  <div ref="bubbleContainer"> </div>
</template>

<script>
import $ from 'jquery';
import './Charts/jQueryCharts/waterBubble'

export default {
  name: 'Level',
  props: {
    options: {
      type: Object,
      required: true
    }
  },
  mounted() {
    this.renderBubble();
  },
  watch: {
    options: {
      deep: true,
      handler() {
        this.renderBubble();
      }
    }
  },
  methods: {
    renderBubble() {
      const defaultOptions = {
        radius: 80,
        lineWidth: undefined,
        data: 0.9, 
        waterColor: 'rgba(25, 139, 201, 1)',
        textColor: 'rgba(06, 85, 128, 0.8)',
        font: '',
        wave: true,
        txt: undefined,
        animation: true
      };
      const options = { ...defaultOptions, ...this.options };

      $(this.$refs.bubbleContainer).empty();

    const canvas = document.createElement('canvas');
    canvas.id = "waterBubbleCanvas"
    this.$refs.bubbleContainer.appendChild(canvas);
    $(canvas).waterbubble(options)
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>



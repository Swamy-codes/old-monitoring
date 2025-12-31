<template>
<div>
  <!-- <Navbar /> -->
  <div class="box-container">
    <h1 class="heading">Smart Metal Cutting and Fabrication Shop</h1>
  </div>
  <div class="flex justify-center items-center">
    <div class="grid grid-cols-4 gap-4">
      <div class="card col-span-2 bg-white rounded-lg shadow-lg p-6" style="width: 350px; height: 620px;">
        <div class="text-overline mb-4">
          <h3>Status Of Machines</h3>
        </div>
        <table class="w-full">
          <tr>
            <td class="border px-4 py-2">Running</td>
            <td class="border px-4 py-2"><span class="status-dot status-dot-Running"></span></td>
          </tr>
          <tr>
            <td class="border px-4 py-2">Idle Mode</td>
            <td class="border px-4 py-2"><span class="status-dot status-dot-Idle"></span></td>
          </tr>
          <tr>
            <td class="border px-4 py-2">Switch Off</td>
            <td class="border px-4 py-2"><span class="status-dot status-dot-Off"></span></td>
          </tr>
          <tr>
            <td class="border px-4 py-2">Maintenance</td>
            <td class="border px-4 py-2"><span class="status-dot status-dot-Maintenance"></span></td>
          </tr>
        </table>
      </div>

      <div class="col-span-2 relative"  style="left: -250px;">
        <div class="grid grid-cols-3 gap-4 justify-center">
          <div v-for="card in smallCards" :key="card.id" class="bg-white rounded-lg shadow-lg p-6"
            style="width: 300px; height: 300px;">
            <img class="w-full h-3/5 object-cover rounded-lg mb-4" :src="card.imageUrl" alt="Machine Image" />
            <p class="text-gray-700">{{ card.text }}</p>
            <div class="flex items-center justify-center mt-4">
              <span class="status-dot mr-2" :class="'status-dot-' + card.status"></span>
              <span>{{ card.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import Navbar from "../components/Navbar.vue";
import CNCSheetMetal from "../assets/MachineImages/CNC_TurningJE-06-LM-XL-removebg-preview.png";
import CNCPress from "../assets/MachineImages/CNC_Milling-540V-removebg-preview.png";
import CNCMilling from "../assets/MachineImages/Cylindrical_Grinder-GCU-350-removebg-preview.png";
import CNCCylindrical from "../assets/MachineImages/LS20240529163413.png";
import CNCSheet from "../assets/MachineImages/LS20240529163402.png";

export default {
  data() {
    return {
      Navbar:Navbar,
      smallCards: [
        { id: 1, imageUrl: CNCSheetMetal, text: "CNC Sheet Metal Cutting Machine", status: "Running" },
        { id: 2, imageUrl: CNCMilling, text: "CNC Milling Machine", status: "Idle" },
        { id: 3, imageUrl: CNCCylindrical, text: "CNC Cylindrical Grinding Machine", status: "Maintenance" },
        { id: 4, imageUrl: CNCPress, text: "CNC Press for Sheet Metal Cutting", status: "Off" },
        { id: 5, imageUrl: CNCSheet, text: "CNC Sheet Metal Cutting Machine", status: "Running" },
      ],
    };
  },
};
</script>

<style scoped>
.box-container {
  border: 2px solid #ccc;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  padding: 10px;
  text-align: center;
  display: inline-block;
  max-width: 110%;
  width: auto;
  margin-left: 800px;
  margin-top: 20px;
}

.heading {
  font-size: 28px;
  margin-bottom: 5px;
  margin-top: 10px;
  font-weight: bold;
  text-align: center;
  font-family: "Roboto", sans-serif;
  background: linear-gradient(to right, #f04317, #442b22);
  -webkit-background-clip: text;
  -moz-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.card {
  margin-left: 150px;
}

.flex {
  margin-top: 40px;
}

.grid-cols-3 {
  margin: 0 auto;
}

.col-span-2.relative {
  justify-self: center;
}

p {
  text-align: center;
  font-weight: bold;
  color: rgb(226, 142, 142);
}

h3 {
  text-align: center;
  font-weight: bold;
  font-size: 26px;
  color: rgb(75, 7, 7);
}

.status-dot {
  width: 14px;
  height: 14px;
  display: inline-block;
  border-radius: 50%;
  margin-left: 5px;
  border: 2px solid #000;
  vertical-align: middle;
}

.status-dot-Running {
  background-color: green;
}

.status-dot-Idle {
  background-color: yellow;
}

.status-dot-Off {
  background-color: red;
}

.status-dot-Maintenance {
  background-color: orange;
}
.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>

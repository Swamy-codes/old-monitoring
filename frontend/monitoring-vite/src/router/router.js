import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '../layout/DefaultLayout.vue'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Blog from '../views/Blog.vue'



const routes = [
    {
        path: '/',
        // component: Home,
        children: [
        {
            path:"/",
            name:"defaultLayout",
            component:DefaultLayout
            },
            {
            path:"/about",
            name:"about",
            component:About
            },
            {
            path:"/blog",
            name:"blog",
            component:Blog
              },
        ]
    }

]

const router = createRouter({
    history: createWebHistory(),
    routes,
  });
  
  export default router;
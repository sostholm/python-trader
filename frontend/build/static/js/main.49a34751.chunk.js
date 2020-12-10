(this.webpackJsonpfrontend=this.webpackJsonpfrontend||[]).push([[0],{175:function(e,t,n){},176:function(e,t,n){},286:function(e,t,n){"use strict";n.r(t);var a=n(4),r=n(0),i=n.n(r),o=n(16),c=n.n(o),s=(n(175),n(10)),u=n(116),l=(n.p,n(176),n(27)),d=n(152),f=n(159),b=n(334),j=n(155),p=n(19),O=n.n(p),h=n(25),g=n(322),m=n(338),x=n(331),v=Object(g.a)((function(e){return{root:{display:"flex",flexFlow:"column","& > *":{margin:e.spacing(1),width:"25ch"}}}}));function w(e){var t=Object(r.useState)(""),n=Object(s.a)(t,2),i=n[0],o=n[1],c=Object(r.useState)(""),u=Object(s.a)(c,2),l=u[0],d=u[1],f=v();if(e.loggedIn)return Object(a.jsx)(a.Fragment,{});var b=function(){var t=Object(h.a)(O.a.mark((function t(){var n;return O.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return console.log("Sending websocket data"),t.next=3,fetch("/login",{method:"POST",body:JSON.stringify({username:i,password:l})}).then((function(e){return e.json()}));case 3:n=t.sent,e.setToken(n.token),localStorage.setItem("token",n.token),e.setLoggedIn(!0,e.setView("Balance"));case 7:case"end":return t.stop()}}),t)})));return function(){return t.apply(this,arguments)}}();return Object(a.jsxs)("div",{className:f.root,children:[Object(a.jsx)(m.a,{id:"outlined-basic",variant:"outlined",value:i,onChange:function(e){return o(e.target.value)},label:"Username"}),Object(a.jsx)(m.a,{id:"outlined-basic",variant:"outlined",value:l,onChange:function(e){return d(e.target.value)},label:"Password",type:"password"}),Object(a.jsx)(x.a,{variant:"contained",color:"primary",onClick:b,children:"Login"})]})}n(335),n(332),n(339),n(328),Object(g.a)((function(e){return{root:{display:"flex",flexFlow:"column","& > *":{margin:e.spacing(1),width:"25ch"}},formControl:{margin:e.spacing(1),minWidth:120}}}));Object(g.a)((function(e){return{root:{display:"flex",flexFlow:"column","& > *":{margin:e.spacing(1),width:"25ch"}},formControl:{margin:e.spacing(1),minWidth:120}}}));Object(g.a)((function(e){return{root:{display:"flex",flexFlow:"column","& > *":{margin:e.spacing(1),width:"25ch"}},formControl:{margin:e.spacing(1),minWidth:120}}}));var y=n(61),k=n(157);function S(){var e=Object(y.a)(["\nquery{\n    me{\n        lastUpdate\n    }\n  }\n"]);return S=function(){return e},e}var C=Object(l.gql)(S());function L(e){var t=Object(r.useState)(!0),n=Object(s.a)(t,2),i=n[0],o=n[1],c=Object(l.useQuery)(C,{pollInterval:5e4}),u=c.loading,d=c.error,f=c.data;return Object(r.useEffect)((function(){if(f&&"me"in f&&"lastUpdate"in f.me){var e=new Date(1e3*f.me.lastUpdate);new Date-e>12e5?o(!1):!i&&new Date-e<12e5&&o(!0)}}),[f]),u?Object(a.jsx)("p",{children:"Loading..."}):d?Object(a.jsx)("p",{children:"Error :("}):Object(a.jsx)("svg",{width:"50",height:"50",viewBox:"0 0 200 200",children:Object(a.jsxs)("g",{transform:"translate(100 100)",children:[Object(a.jsx)("path",{transform:"translate(-50 -50)",fill:i?"tomato":"gray",d:"M92.71,7.27L92.71,7.27c-9.71-9.69-25.46-9.69-35.18,0L50,14.79l-7.54-7.52C32.75-2.42,17-2.42,7.29,7.27v0 c-9.71,9.69-9.71,25.41,0,35.1L50,85l42.71-42.63C102.43,32.68,102.43,16.96,92.71,7.27z"}),i&&Object(a.jsx)("animateTransform",{attributeName:"transform",type:"scale",values:"1; 1.5; 1.25; 1.5; 1.5; 1; 1; 1; 1; 1;",dur:"2s",repeatCount:"indefinite",additive:"sum"})]})})}var T=["#1b9e77","#d95f02","#7570b3","#e7298a","#66a61e","#e6ab02","#a6761d","#666666","#a6cee3","#1f78b4","#b2df8a","#33a02c","#fb9a99","#e31a1c","#fdbf6f","#ff7f00","#cab2d6","#6a3d9a","#ffff99","#b15928","#fbb4ae","#b3cde3","#ccebc5","#decbe4","#fed9a6","#ffffcc","#e5d8bd","#fddaec","#f2f2f2"];function F(){var e=Object(y.a)(["\nquery{\n    me{\n      portfolio{\n        currency\n        total\n        usd\n      }\n    }\n  }\n"]);return F=function(){return e},e}var I=Object(g.a)((function(e){return{root:{display:"flex",flexFlow:"column","& > *":{margin:e.spacing(1),width:"25ch"}},formControl:{margin:e.spacing(1),minWidth:120}}})),A=Object(l.gql)(F());function B(e){var t=Object(r.useState)(),n=Object(s.a)(t,2),i=(n[0],n[1],Object(r.useState)()),o=Object(s.a)(i,2),c=o[0],u=o[1],d=Object(r.useState)(),f=Object(s.a)(d,2),b=f[0],j=f[1],p=I(),O=Object(l.useQuery)(A,{pollInterval:1e4}),h=O.loading,g=O.error,m=O.data;return Object(r.useEffect)((function(){if(m){var e=0,t=Object.values(m.me.portfolio).filter((function(e){return parseFloat(e.usd)>1}));Object.values(t).map((function(t){return e+=parseFloat(t.usd)}));var n={};Object.values(t).map((function(e){return n[e.currency]=0})),Object.values(t).map((function(e){return n[e.currency]+=parseFloat(e.usd)})),(n=Object.keys(n).map((function(e){return[e,n[e]]}))).sort((function(e,t){return e[1]>t[1]?1:t[1]>e[1]?-1:0})).reverse(),j({datasets:[{data:n.map((function(e){return e[1]})),backgroundColor:Object.values(t).map((function(e,t){return T[t]})),label:"Value in USD"}],labels:n.map((function(e){return e[0]}))}),u(e)}}),[m]),h?Object(a.jsx)("p",{children:"Loading..."}):g?Object(a.jsx)("p",{children:"Error :("}):Object(a.jsxs)("div",{className:p.root,children:[Object(a.jsx)(L,{}),Object(a.jsx)("div",{children:c}),Object(a.jsx)(k.HorizontalBar,{width:"90%",data:b})]})}var N=n(160);Notification.requestPermission((function(e){console.log("Notification permission status:",e)}));var P=function(e){var t=(e+"=".repeat((4-e.length%4)%4)).replace(/\-/g,"+").replace(/_/g,"/"),n=window.atob(t);return Uint8Array.from(Object(N.a)(n).map((function(e){return e.charCodeAt(0)})))}("BOnPOdBMs6jPhfJ_F9EpeyiPOc2dX4niC6-V_zSZcRSn2TwRkI4i_TeLqxiSTSiPgm89355SeAZFZnJp9QMfWqY");function E(e){return W.apply(this,arguments)}function W(){return(W=Object(h.a)(O.a.mark((function e(t){return O.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.pushManager.subscribe({userVisibleOnly:!0,applicationServerKey:P}).then((function(e){return console.log("Endpoint URL: ",e.endpoint),console.log("Origin: ",new URL(e.endpoint).origin),t(e.toJSON()),e})).catch((function(e){"denied"===Notification.permission?console.warn("Permission for notifications was denied"):console.error("Unable to subscribe to push",e)}))}));case 1:case"end":return e.stop()}}),e)})))).apply(this,arguments)}function q(){var e=Object(y.a)(["\nmutation($endpoint: String!, $expirationTime: Int!, $p256dh: String!, $auth: String!){\n  addSubscription(endpoint: $endpoint, expirationTime: $expirationTime, p256dh: $p256dh, auth: $auth){\n    stuff\n  }\n}\n"]);return q=function(){return e},e}var U=Object(g.a)((function(e){return{root:{display:"flex",flexFlow:"column","& > *":{margin:e.spacing(1),width:"25ch"}},formControl:{margin:e.spacing(1),minWidth:120}}})),$=Object(l.gql)(q());function D(e){var t=Object(l.useMutation)($),n=Object(s.a)(t,2),r=n[0],i=(n[1].data,U());if(e.invisible)return Object(a.jsx)(a.Fragment,{});function o(){return(o=Object(h.a)(O.a.mark((function e(){return O.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,E((function(e){return r({variables:{endpoint:e.endpoint,expirationTime:e.expirationTime,p256dh:e.keys.p256dh,auth:e.keys.auth}})}));case 2:console.log("this");case 3:case"end":return e.stop()}}),e)})))).apply(this,arguments)}return Object(a.jsx)("div",{className:i.root,children:Object(a.jsx)(x.a,{variant:"contained",color:"primary",onClick:function(){return o.apply(this,arguments)},children:"Subscribe Push Notification"})})}var M=n(89),V=n(7),J=n(336),_=n(333),z=n(158),R=n.n(z),Q=n(330),Z=n(289),H=n(340),K=Object(g.a)({list:{width:250},fullList:{width:"auto"},menuButton:{position:"absolute",left:"2rem",top:"2rem"}});function X(e){var t,n=K(),r=i.a.useState(!1),o=Object(s.a)(r,2),c=o[0],u=o[1],l=function(e){return function(t){(!t||"keydown"!==t.type||"Tab"!==t.key&&"Shift"!==t.key)&&u(e)}};return Object(a.jsxs)("div",{children:[Object(a.jsx)("div",{className:n.menuButton,children:Object(a.jsx)(_.a,{color:"primary","aria-label":"upload picture",component:"span",onClick:l(!0),children:Object(a.jsx)(R.a,{})})}),Object(a.jsx)(J.a,{anchor:"left",open:c,onClose:l(!1),onOpen:l(!0),children:(t="left",Object(a.jsx)("div",{className:Object(V.a)(n.list,Object(M.a)({},n.fullList,"top"===t||"bottom"===t)),role:"presentation",onClick:l(!1),onKeyDown:l(!1),children:Object(a.jsxs)(Q.a,{children:[e.views?e.views.map((function(t,n){return Object(a.jsx)(Z.a,{button:!0,onClick:function(){return e.setView(t.text)},children:Object(a.jsx)(H.a,{primary:t.text})},t.key)})):null,Object(a.jsx)(Z.a,{button:!0,onClick:function(){return e.logout()},children:Object(a.jsx)(H.a,{primary:"Logout"})},"logout")]})}))})]})}Object(g.a)((function(e){return{scene:{width:"210px",height:"140px",position:"relative",perspective:"1000px"},carousel:{width:"100%",height:"100%",position:"absolute",transformStyle:"preserve-3d"},carousel__cell:{position:"absolute",width:"190px",height:"120px",left:"10px",top:"10px"}}}));var Y,G=Object(f.a)({palette:{type:"dark"}});Y="https://pine64:8000";var ee=function(){var e=Object(r.useState)(localStorage.getItem("token")),t=Object(s.a)(e,2),n=t[0],i=t[1],o=Object(r.useState)(),c=Object(s.a)(o,2),f=c[0],p=c[1],O=Object(r.useState)(!1),h=Object(s.a)(O,2),g=h[0],m=h[1],x=Object(r.useState)("Login"),v=Object(s.a)(x,2),y=v[0],k=v[1],S=Object(r.useState)(!1),C=Object(s.a)(S,2),L=(C[0],C[1],function(){localStorage.removeItem("token"),i(null),window.location.reload()});return Object(r.useEffect)((function(){localStorage.getItem("token")&&m(!0)}),[]),Object(r.useEffect)((function(){if(n){var e=parseInt((new Date).getTime()/1e3),t=Object(j.a)(n).exp;if(!(t<e)){var a=setTimeout((function(){L()}),t-1e3*e);return function(){clearTimeout(a)}}L()}else n||"Login"===y||k("Login")}),[n]),Object(r.useEffect)((function(){g||"Login"===y?g&&!f&&(p(function(){var e=Object(l.createHttpLink)({uri:Y+"/graphql"}),t=Object(d.a)((function(e,t){var n=t.headers,a=localStorage.getItem("token");return{headers:Object(u.a)(Object(u.a)({},n),{},{authorization:a?"Bearer ".concat(a):""})}}));return new l.ApolloClient({link:t.concat(e),cache:new l.InMemoryCache})}()),k("Balance")):k("Login")}),[g]),Object(a.jsx)("div",{className:"App",children:Object(a.jsx)("div",{className:"App-header",children:Object(a.jsxs)(b.a,{theme:G,children:["Login"===y&&Object(a.jsx)(w,{loggedIn:g,setLoggedIn:m,setToken:i,setView:k}),f&&Object(a.jsxs)(l.ApolloProvider,{client:f,children:[Object(a.jsx)(X,{views:[{key:"Login",text:"Login"},{key:"AddAccount",text:"Add Account"},{key:"Add Wallet",text:"Add Wallet"},{key:"Add Token",text:"Add Token"},{key:"Balance",text:"Balance"},{key:"Settings",text:"Settings"}],setView:k,logout:L}),g&&"Balance"===y&&Object(a.jsx)(B,{}),g&&"Settings"==y&&Object(a.jsx)(D,{})]})]})})})},te=function(e){e&&e instanceof Function&&n.e(3).then(n.bind(null,343)).then((function(t){var n=t.getCLS,a=t.getFID,r=t.getFCP,i=t.getLCP,o=t.getTTFB;n(e),a(e),r(e),i(e),o(e)}))};c.a.render(Object(a.jsx)(i.a.StrictMode,{children:Object(a.jsx)(ee,{})}),document.getElementById("root")),te()}},[[286,1,2]]]);
//# sourceMappingURL=main.49a34751.chunk.js.map
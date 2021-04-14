// register modal component
Vue.component("modal", {
    template: "#modal-template"
  });
 
 var app = new Vue({
   el: "#app",
 
   //------- data --------
   data: {
     serviceURL: "https://cs3103.cs.unb.ca:45020",
     // Whether or not the user is authenticated
     authenticated: false,
     userData: null,
     presentData: null,
     // Who the logged user is
     loggedIn: null,
     // All info about the current user
     currentUser: null,
     modalAdd: false,
     modalUpdate: false,
     input: {
       username: "",
       password: ""
     },
     presentForm: {
      presentName: "",
      presentDesc: "",
      presentPrice: ""
     },
     selectedPresent: {
       name: "",
       desc: "",
       price: "",
       owner: "",
       presentID: ""
     },
     selectedUser: {
       name: "",
       isAdmin: "",
       userId: ""
     }
   },

   //------- methods --------
   methods: {
     login() {
       if (this.input.username != "" && this.input.password != "") {

         // Hit LDAP endpoint for initial authentication
         axios
         .post(this.serviceURL+"/signin", {
             "username": this.input.username,
             "password": this.input.password
         })
         .then(response => {
             if (response.data.status == "success") {
               this.authenticated = true;
               this.loggedIn = response.data.user_id;

               // Get user object from the database
               this.login_getUserByName(this.input.username);
             }
         })
         .catch(e => {
             alert("The username or password was incorrect, try again");
             this.input.password = "";
             console.log(e);
         });
       } else {
         alert("A username and password must be present");
       }
     },

     login_getUserByName(name) {
         // Get user object from the database
         axios
         .get(this.serviceURL+"/username/"+this.input.username)
         .then(response => {
            this.currentUser = response.data.user;
            this.getUsers();
        })
        .catch(e => {
          if(e.response) {
            if(e.response.status == 404) {
              this.login_CreateNewUser(name);
            }
            else {
              alert("An internal error occured, please try again");
              this.input.password = "";
              console.log(e);
            }
          } else {
            alert("An internal error occured, please try again");
            this.input.password = "";
            console.log(e);
          }
        })
     },

     login_GetUserById(ID) {
        // Get newly created user object
        axios
        .get(this.serviceURL+"/user/" + ID)
        .then(response => {
            this.currentUser = response.data.user
            this.getUsers();
        })
        .catch(e => {
          alert("An internal error occured, please try again");
          this.input.password = "";
          console.log(e);
        })
     },

     login_CreateNewUser(name) {
        // User doesn't exist, create it
        axios
        .post(this.serviceURL+"/users", {
          "Name": name
        })
        .then(response => {
          this.login_GetUserById(response.data.userID)
        })
        .catch(e => {
          alert("An internal error occured (regis), please try again");
          this.input.password = "";
          console.log(e);
          })
     },

     logout() {
        this.authenticated = false;
        this.loggedIn = null;
        location.reload();
     },
 
     getUsers() {
       axios
       .get(this.serviceURL+"/users")
       .then(response => {
           this.userData = response.data.users;
       })
       .catch(e => {
         alert("Unable to load users list");
         console.log(e);
       });
     },

     getPresentsByUser(userId) {
      this.selectedUser.userID = userId;

      axios
      .get(this.serviceURL+"/presents/"+this.selectedUser.userID)
      .then(response => {
          this.presentData = response.data.presents;
      })
      .catch(e => {
        alert("Unable to load the present data");
        console.log(e);
      });
    },
 
     deletePresent(presentId) {
       axios 
      .delete(this.serviceURL+"/present/"+presentId)
      .then(response => {
        this.getPresentsByUser(this.currentUser.userID);
      })
      .catch(e => {
        console.log(e);
      });
     },
 
     selectPresent(presentId) {
      //   this.showModal();
       for (x in this.presentData) {
         if (this.presentData[x].presentID == presentId) {
           this.selectedPresent = this.presentData[x];
         }
       }
     },
     
     addPresent() {
      if (this.presentForm.presentName != "" && this.presentForm.presentPrice != "") {
        axios
        .post(this.serviceURL+"/presents/" + this.currentUser.userID, {
            "presentName": this.presentForm.presentName,
            "presentDesc": this.presentForm.presentDesc,
            "presentPrice": this.presentForm.presentPrice
        })
        .then(response => {
            if (response.data.status == "success") {
              this.presentForm.presentName = "";
              this.presentForm.presentDesc = "";
              this.presentForm.presentPrice = "";
              this.getPresentsByUser(this.currentUser.userID);
              
              this.hideModal();
              alert("Present Added Successfully");
            }
        })
        .catch(e => {
            alert("Unable to register present, please try again");
            console.log(e);
        });
      } else {
        alert("Present must have a name and a price");
      }
    },
 
     updatePresent(updatedPresentId) {
      if (this.presentForm.presentName != "" && this.presentForm.presentPrice != "") {
        axios
        .post(this.serviceURL+"/present/" + updatedPresentId, {
            "presentName": this.presentForm.presentName,
            "presentDesc": this.presentForm.presentDesc,
            "presentPrice": this.presentForm.presentPrice
        })
        .then(response => {
            if (response.data.status == "success") {
              this.presentForm.presentName = "";
              this.presentForm.presentDesc = "";
              this.presentForm.presentPrice = "";
              this.getPresentsByUser(this.currentUser.userID);
              
              this.hideModal();
              alert("Present Updated Successfully");
            }
        })
        .catch(e => {
            alert("Unable to register present, please try again");
            console.log(e);
        });
      } else {
        alert("Present must have a name and a price");
      }
     },
 
     showModalAdd() {
       this.modalAdd = true;
     },

     showModalUpdate() {
      this.modalUpdate = true;
    },
 
     hideModal() {
       if (this.modalAdd) {
        this.modalAdd = false;
       }
       if (this.modalUpdate) {
        this.modalUpdate = false;
       }
     },

     formatPrice(value) {
      let val = (value/1).toFixed(2) //.replace('.', ',')
      return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
  }
 
   }
   //------- END methods --------
 
 });
 
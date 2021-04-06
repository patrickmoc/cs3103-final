// register modal component
Vue.component("modal", {
    template: "#modal-template"
  });
 
 var app = new Vue({
   el: "#app",
 
   //------- data --------
   data: {
     serviceURL: "https://cs3103.cs.unb.ca:45020",
     //      serviceURL: "https://cs3103.cs.unb.ca:<probably your port number>",
     // Is the user authenticated
     authenticated: false,
     userData: null,
     presentData: null,
     // Session ID
     loggedIn: null,
     // All info about the current user
     currentUser: null,
     modal: false,
     input: {
       username: "",
       password: "",
     },
     presentForm: {
      presentName: "",
      presentDesc: "",
      presentPrice: "",
     },
     selectedPresent: {
       name: "",
       desc: "",
       price: "",
       owner: "",
       presentId: ""
     },
     selectedUser: {
       name: "",
       isAdmin: "",
       userId: ""
     }
   },
   //------- lifecyle hooks --------
   /*mounted: function() {
     axios
     .get(this.serviceURL+"/signin")
     .then(response => {
       if (response.data.status == "success") {
         this.authenticated = true;
         this.loggedIn = response.data.user_id;
       }
     })
     .catch(error => {
         this.authenticated = false;
         console.log(error);
     });
   },*/
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
               axios
               .get(this.serviceURL+"/username/"+this.input.username)
               .then(response => {
                 if(response.data.status == "success") {
                    this.currentUser = response.data.user
                 }
                 else {

                   // User doesn't exist, create it
                   axios
                   .post(this.serviceURL+"/users/", {
                     "Name": this.input.username
                   })
                   .then(response => {
                     if(response.data.status == "success") {

                       // Get newly created user object
                        axios
                        .get(this.serviceURL+"/user/" + response.data.userID)
                        .then(response => {
                          this.currentUser = response.data.user
                        })
                     }
                     else {

                       // If this happens something has gone horribly wrong
                       this.authenticated = false;
                       loggedIn = null;
                       alert("a bruh moment has occurred, please try again");
                       this.input.password = "";
                     }
                   })
                 }
               })
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
 
     logout() {
       axios
       .delete(this.serviceURL+"/signin")
       .then(response => {
            this.authenticated = false;
            this.loggedIn = null;
            location.reload();
       })
       .catch(e => {
         console.log(e);
       });
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

     getPresentsByUser() {
      axios
      .get(this.serviceURL+"/users/"+userId)
      .then(response => {
          this.presentData = response.data.presents;
      })
      .catch(e => {
        alert("Unable to load the present data");
        console.log(e);
      });
    },
 
     deletePresent(presentId) {
       alert("WHEN THE IMPOSTER IS SUS");
     },
 
 
     selectPresent(presentId) {
         this.showModal();
       for (x in this.presentData) {
         if (this.presentData[x].presentID == presentId) {
           this.selectedPresent = this.presentData[x];
         }
       }
     },
     
     addPresent() {
       console.log(`${this.input.presentName} YEA BOYEEEEEE`);
      if (this.presentForm.presentName != "" && this.presentForm.presentPrice != "") {
        axios
        .post(this.serviceURL+"/users", {
            "presentName": this.presentForm.presentName,
            "presentDesc": this.presentForm.presentDesc,
            "presentPrice": this.presentForm.presentPrice

        })
        .then(response => {
            if (response.data.status == "success") {
              this.hideModal();
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
 
     updatePresent(updatedPresent) {
       // TODO: use axios.update to send the updated record to the service
     },
 
     showModal() {
       this.modal = true;
     },
 
     hideModal() {
       this.modal = false;
     }
 
   }
   //------- END methods --------
 
 });
 
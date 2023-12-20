const mongoose = require('mongoose');

const AdminSchema = mongoose.Schema({
        name: {
            type: String,

    },
    personalnr: {
        type: String,
},
    password: {
            type: String,
    }, 
    etat: {
        type: String,
}

}, {
    timestamps: true
});

module.exports = mongoose.model('Admin', AdminSchema);
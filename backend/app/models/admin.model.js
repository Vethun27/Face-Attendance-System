const mongoose = require('mongoose');

const AdminSchema = mongoose.Schema({
        name: {
            type: String,

    },

    password: {
            type: String,
    }

}, {
    timestamps: true
});

module.exports = mongoose.model('Admin', AdminSchema);
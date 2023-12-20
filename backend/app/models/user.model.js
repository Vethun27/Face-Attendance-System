const mongoose = require('mongoose');

const UserSchema = mongoose.Schema({
        name: {
            type: String,

    },
    numfeature: {
            type: String,
    }

}, {
    timestamps: true
});

module.exports = mongoose.model('User', UserSchema);
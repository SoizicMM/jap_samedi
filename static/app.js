// Donner des conditions pour améliorer le mdp des utilisateurs

// Fonction permettant de chargé toute la page HTML avant d'éxécuter le script js
$(document).ready(function() {
    // Fonction s'exécutant à chaque fois qu'une touche
    // est relâchée dans le champs mot de passe
    $('#password').on('keyup', function() {
        var password = $(this).val();
        var lowerCaseLetters = /[a-z]/g;
        var upperCaseLetters = /[A-Z]/g;
        var numbers = /[0-9]/g;

        // Vérifier et mettre à jour les conditions de mot de passe
        var lowercasePassed = password.match(lowerCaseLetters) ? true : false;
        var uppercasePassed = password.match(upperCaseLetters) ? true : false;
        var numberPassed = password.match(numbers) ? true : false;

        if (lowercasePassed) {
            $('#lowercase').css('color', 'green');
        } else {
            $('#lowercase').css('color', 'red');
        }

        if (uppercasePassed) {
            $('#uppercase').css('color', 'green');
        } else {
            $('#uppercase').css('color', 'red');
        }

        if (numberPassed) {
            $('#number').css('color', 'green');
        } else {
            $('#number').css('color', 'red');
        }

      // Activer le bouton de soumission si toutes les conditions sont remplies
      if (lowercasePassed && uppercasePassed && numberPassed) {
          $('#submit-btn').prop('disabled', false);
      } else {
          $('#submit-btn').prop('disabled', true);
      }
    });
});
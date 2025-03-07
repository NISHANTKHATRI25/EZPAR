function toggleForm(option) {
            var createTeamForm = document.getElementById('createTeamForm');
            var joinTeamForm = document.getElementById('joinTeamForm');

            if (option === 'create') {
                createTeamForm.style.display = 'block';
                joinTeamForm.style.display = 'none';
            } else {
                createTeamForm.style.display = 'none';
                joinTeamForm.style.display = 'block';
            }
}
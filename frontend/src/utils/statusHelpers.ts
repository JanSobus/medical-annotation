export const getStatusColor = (status: string) => {
  switch (status) {
    case 'not_started':
      return 'bg-gray-100 text-gray-700'
    case 'in_progress':
      return 'bg-blue-100 text-blue-700'
    case 'completed':
      return 'bg-green-100 text-green-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

export const getStatusLabel = (status: string) => {
  switch (status) {
    case 'not_started':
      return 'Not Started'
    case 'in_progress':
      return 'In Progress'
    case 'completed':
      return 'Completed'
    default:
      return status
  }
}


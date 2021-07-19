import "./Empyre.css";


export default function Empyre() {

    const squares = {};
    const terrains = {
        water: "blue",
        desert: "wheat",
        grassland: "green",
        plains: "brown",
    };

    const citizens = [];

    function initSquaresOrSomething() {
        for (let x = 0; x < 10; x++) {
            squares[x] = {};
            for (let y = 0; y < 10; y++) {
                // This gets a random item from the terrains object
                squares[x][y] = {
                    type: Object.keys(terrains)[Math.floor(Math.random() * Object.keys(terrains).length)],
                    buildings: []
                };
            }
        }
    }

    function addBuilding(x, y, building) {
        squares[x][y].buildings.push(building)
    }

    function makeCitizen() {
        const citizen = {
            age: 0,
            food: 0,
            currentlyWorking: false,
            currentlyWorkingTilePosition: [],
        };

        citizens.push(citizen);
    }

    initSquaresOrSomething(squares);
    addBuilding(5, 5, "Palace")
    makeCitizen();

    function getAvailableCitizens() {
        let availableCitizenIndex;

        citizens.forEach((citizen, index) => {
            if (!citizen.currentlyWorking) {
                availableCitizenIndex = index;
                return;
            }
        });
        console.log(`Available Citizen Index: ${availableCitizenIndex}`);
        return availableCitizenIndex;
    }

    function assignCitizen(x, y) {
        let wasWorked = false;
        console.log(citizens);
        citizens.forEach((citizen, index) => {
            if (citizen.currentlyWorkingTilePosition[0] == x &&
                citizen.currentlyWorkingTilePosition[1] == y) {
                citizens[index].currentlyWorking = false;
                citizens[index].currentlyWorkingTilePosition = [];
                wasWorked = true;
            }
        })

        if (wasWorked) return;

        const availableCitizen = getAvailableCitizens();
        if (availableCitizen !== undefined) {
            citizens[availableCitizen].currentlyWorking = true;
            citizens[availableCitizen].currentlyWorkingTilePosition = [x, y];
        }
    }

    return (
        <>
            <h1>Population: {citizens.length}</h1>
            <div className="square-grid">
                {
                    Object.entries(squares).map(
                        ([keyX, value]) =>
                            Object.entries(squares[keyX]).map(([keyY, tile]) =>
                                <div className="square"
                                    onClick={() => assignCitizen(parseInt(keyX), parseInt(keyY))}
                                    style={{ backgroundColor: terrains[tile.type] }}
                                    key={`${keyX}${keyY}`}>{tile.buildings.length ? `${tile.buildings[0]}` : ''}  {keyX} {keyY}
                                </div>)
                    )
                }
            </div>
        </>
    )
}